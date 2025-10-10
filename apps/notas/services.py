from apps.parceiros.models import Parceiro
from apps.processamento.models import JobProcessamento
from apps.notas.models import NotaFiscal, NotaFiscalItem
from apps.financeiro.models import LancamentoFinanceiro
from apps.notas.extractors import ExtractorInterface, ExtractorFactory, InvoiceData
from apps.financeiro.strategies import TipoLancamentoContext
from apps.classificadores.models import get_classifier
from apps.core.observers import Subject
from apps.financeiro.observers import AlertaVencimentoObserver
from apps.dashboard.observers import MetricasFinanceirasObserver
from apps.parceiros.observers import ValidacaoCNPJObserver
from apps.notifications.observers import PushStoreObserver
from decimal import Decimal, InvalidOperation
import logging
from apps.empresa.models import EmpresaNaoClassificada

logger = logging.getLogger(__name__)


class NotaFiscalService(Subject):
    def __init__(self, extractor: ExtractorInterface = None, tipo_lancamento_context: TipoLancamentoContext = None):
        super().__init__()
        self.extractor = extractor
        self.tipo_lancamento_context = tipo_lancamento_context or TipoLancamentoContext()

        # registrar observers padrão
        self.attach(AlertaVencimentoObserver())
        self.attach(MetricasFinanceirasObserver())
        self.attach(ValidacaoCNPJObserver())
        # armazena notificações server-side para clients polling
        try:
            self.attach(PushStoreObserver())
        except Exception:
            # keep backward compatibility if notifications app absent
            pass

    def processar_nota_fiscal_do_job(self, job: JobProcessamento) -> LancamentoFinanceiro:
        # import transaction lazily to avoid top-level import resolution issues in static checks
        from django.db import transaction

        with transaction.atomic():
            minha_empresa = job.empresa

            filename = job.arquivo_original.name
            file_content = job.arquivo_original.read()

            # 1) Tenta LLM primeiro (se disponível e arquivo suportado)
            dados_extraidos: InvoiceData
            llm_sucesso = False
            try:
                dados_extraidos_llm = self._try_extract_with_llm(file_content, filename)
                if dados_extraidos_llm is not None:
                    dados_extraidos = dados_extraidos_llm
                    llm_sucesso = True
                    logger.info("Extração por LLM realizada com sucesso para %s", filename)
                else:
                    raise ValueError("LLM não retornou dados utilizáveis")
            except Exception as e:
                logger.info("LLM indisponível ou falhou (%s). Fazendo fallback para extratores legados.", e)
                # 2) Fallback para extratores existentes
                extractor = self.extractor or ExtractorFactory.get_extractor(filename)
                dados_extraidos = extractor.extract(file_content, filename)

            # Usa strategy para determinar tipo e parceiro
            resultado = self.tipo_lancamento_context.determinar_tipo_e_parceiro(dados_extraidos, minha_empresa)

            # CNPJ não corresponde à empresa autenticada
            if resultado['parceiro_data']['cnpj'] != minha_empresa.cnpj:
                self._handle_unclassified_company(dados_extraidos)
                return None

            parceiro = self._get_or_create_parceiro(**resultado['parceiro_data'])

            nota_fiscal = NotaFiscal.objects.create(
                job_origem=job,
                parceiro=parceiro,
                chave_acesso=getattr(dados_extraidos, 'chave_acesso', None),
                numero=dados_extraidos.numero,
                data_emissao=dados_extraidos.data_emissao,
                valor_total=dados_extraidos.valor_total,
            )

            # Persistir itens da nota, quando disponíveis
            self._persistir_itens_da_nota(nota_fiscal, dados_extraidos)

            status_pendente = get_classifier('STATUS_LANCAMENTO', 'PENDENTE')
            lancamento = LancamentoFinanceiro.objects.create(
                nota_fiscal=nota_fiscal,
                descricao=f"NF {nota_fiscal.numero} - {parceiro.nome}",
                valor=nota_fiscal.valor_total,
                clf_tipo=resultado['tipo_lancamento'],
                clf_status=status_pendente,
                data_vencimento=dados_extraidos.data_vencimento,
            )

            # notificar observers sobre o lançamento criado
            self.notify('lancamento_created', lancamento=lancamento)

            return lancamento

    def _get_or_create_parceiro(self, cnpj: str, nome: str, clf_tipo) -> Parceiro:
        parceiro, created = Parceiro.objects.get_or_create(cnpj=cnpj, defaults={'nome': nome, 'clf_tipo': clf_tipo})
        if not created:
            update_fields = []
            if parceiro.nome != nome:
                parceiro.nome = nome
                update_fields.append('nome')
            if parceiro.clf_tipo_id != clf_tipo.id:
                parceiro.clf_tipo = clf_tipo
                update_fields.append('clf_tipo')
            if update_fields:
                parceiro.save(update_fields=update_fields)

        # notificar observers sobre parceiro criado/atualizado
        self.notify('parceiro_created_or_updated', parceiro=parceiro)

        return parceiro

    def _handle_unclassified_company(self, dados_extraidos: InvoiceData):
        logger.info(f"CNPJ não corresponde. Salvando como empresa não classificada: {dados_extraidos.destinatario_cnpj}")
        EmpresaNaoClassificada.objects.update_or_create(
            cnpj=dados_extraidos.destinatario_cnpj,
            defaults={
                'nome_fantasia': dados_extraidos.destinatario_nome,
                'razao_social': dados_extraidos.destinatario_nome,
                'uf': '',
                'cidade': '',
                'logradouro': '',
                'numero': '',
                'bairro': '',
                'cep': '',
                'telefone': '',
                'email': ''
            }
        )

    # ---------------------------------------------------------------------
    # Persistência de Itens
    # ---------------------------------------------------------------------
    def _persistir_itens_da_nota(self, nota_fiscal: NotaFiscal, dados_extraidos) -> None:
        """
        Cria registros de NotaFiscalItem a partir dos dados extraídos quando disponíveis.

        Compatível com:
        - Estruturas dict
        - Objetos com atributos (ex.: Pydantic schemas do módulo LLM)
        - Campos possíveis: 'produtos' (preferencial) ou 'itens'
        """
        try:
            itens = None
            if hasattr(dados_extraidos, 'produtos'):
                itens = getattr(dados_extraidos, 'produtos') or []
            elif hasattr(dados_extraidos, 'itens'):
                itens = getattr(dados_extraidos, 'itens') or []
            elif isinstance(dados_extraidos, dict):
                itens = dados_extraidos.get('produtos') or dados_extraidos.get('itens') or []
            else:
                itens = []

            if not itens:
                logger.info("Nenhum item de nota encontrado para persistir.")
                return

            def _get_attr(obj, name, default=None):
                if isinstance(obj, dict):
                    return obj.get(name, default)
                return getattr(obj, name, default)

            created_count = 0
            for item in itens:
                descricao = _get_attr(item, 'descricao') or _get_attr(item, 'nome') or 'Item'
                quantidade = _get_attr(item, 'quantidade') or 0
                valor_unitario = _get_attr(item, 'valor_unitario') or _get_attr(item, 'preco_unitario') or 0
                valor_total = _get_attr(item, 'valor_total') or _get_attr(item, 'preco_total') or 0

                # Converte para Decimal com segurança
                try:
                    qtd = Decimal(str(quantidade))
                except (InvalidOperation, TypeError, ValueError):
                    qtd = Decimal('0')
                try:
                    v_unit = Decimal(str(valor_unitario))
                except (InvalidOperation, TypeError, ValueError):
                    v_unit = Decimal('0')
                try:
                    v_total = Decimal(str(valor_total))
                except (InvalidOperation, TypeError, ValueError):
                    v_total = (qtd * v_unit).quantize(Decimal('0.01')) if qtd and v_unit else Decimal('0')

                NotaFiscalItem.objects.create(
                    nota_fiscal=nota_fiscal,
                    descricao=str(descricao)[:255],
                    quantidade=qtd,
                    valor_unitario=v_unit,
                    valor_total=v_total,
                )
                created_count += 1

            logger.info("%s itens de nota persistidos para NF %s.", created_count, nota_fiscal.numero)
        except Exception:
            logger.exception("Falha ao persistir itens da nota para NF %s.", nota_fiscal.numero)

    # ---------------------------------------------------------------------
    # Integração com LLM (Gemini/LangChain)
    # ---------------------------------------------------------------------
    def _try_extract_with_llm(self, file_content: bytes, filename: str) -> InvoiceData | None:
        """
        Tenta extrair dados via pipeline LLM. Em caso de sucesso, retorna um InvoiceData
        compatível com as strategies e persistência atuais; caso contrário, retorna None.
        """
        # Suporte apenas para PDF/Imagens
        ext = filename.lower().split('.')[-1]
        if ext not in ['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp']:
            return None

        try:
            from apps.notas.llm import GeminiProvider, DocumentProcessor, TipoDocumento
        except Exception as e:
            logger.debug("Módulo LLM indisponível: %s", e)
            return None

        # Instancia provider e processor
        try:
            llm = GeminiProvider()
            processor = DocumentProcessor(llm_provider=llm)
        except Exception as e:
            logger.debug("Falha ao iniciar provider LLM: %s", e)
            return None

        # Executa processamento
        result = processor.process_file(file_content, filename)
        if not result.success:
            logger.info("LLM não conseguiu processar %s: %s", filename, result.error)
            return None

        # Extrato financeiro não é suportado neste fluxo de nota fiscal
        if result.tipo_documento == TipoDocumento.EXTRATO_FINANCEIRO:
            logger.info("Documento %s classificado como extrato - ignorando no fluxo de NF.", filename)
            return None

        doc = result.dados_extraidos
        from datetime import date as _date

        # Adapter para shapes esperadas pelo sistema (InvoiceData)
        if result.tipo_documento == TipoDocumento.NF_PRODUTO:
            # NotaFiscalProduto
            numero = getattr(doc, 'numero_nota', None) or getattr(doc, 'chave_acesso', 'S/NUM')
            data_emissao = getattr(doc, 'data_emissao', None) or _date.today()
            # Para não quebrar o campo obrigatório de vencimento, usa data_emissao como fallback
            data_vencimento = getattr(doc, 'data_vencimento', None) or data_emissao
            emissor = getattr(doc, 'emissor', None)
            destinatario = getattr(doc, 'destinatario', None)

            inv = InvoiceData(
                numero=str(numero),
                remetente_cnpj=(getattr(emissor, 'cnpj', None) or ""),
                remetente_nome=(getattr(emissor, 'nome', None) or ""),
                destinatario_cnpj=(getattr(destinatario, 'cnpj', None) or getattr(destinatario, 'cpf', None) or ""),
                destinatario_nome=(getattr(destinatario, 'nome', None) or ""),
                valor_total=getattr(doc, 'valor_total', None) or getattr(doc, 'valor_produtos', None),
                data_emissao=data_emissao,
                data_vencimento=data_vencimento,
            )
            # Anexa produtos para persistir itens
            setattr(inv, 'produtos', getattr(doc, 'produtos', None))
            # Se disponível, anexa a chave de acesso para idempotência/persistência
            setattr(inv, 'chave_acesso', getattr(doc, 'chave_acesso', None))
            return inv

        if result.tipo_documento == TipoDocumento.NF_SERVICO:
            # NotaFiscalServico
            numero = getattr(doc, 'numero_nota', None) or 'S/NUM'
            data_emissao = getattr(doc, 'data_emissao', None) or _date.today()
            data_vencimento = getattr(doc, 'data_vencimento', None) or data_emissao
            prestador = getattr(doc, 'prestador', None)
            tomador = getattr(doc, 'tomador', None)

            # Para valor_total, preferimos valor_liquido se disponível
            valor_total = getattr(doc, 'valor_liquido', None) or getattr(doc, 'valor_servico', None)

            inv = InvoiceData(
                numero=str(numero),
                remetente_cnpj=(getattr(prestador, 'cnpj', None) or ""),
                remetente_nome=(getattr(prestador, 'nome', None) or ""),
                destinatario_cnpj=(getattr(tomador, 'cnpj', None) or getattr(tomador, 'cpf', None) or ""),
                destinatario_nome=(getattr(tomador, 'nome', None) or ""),
                valor_total=valor_total,
                data_emissao=data_emissao,
                data_vencimento=data_vencimento,
            )
            # NFSe normalmente não tem itens estruturados; mantém compat
            setattr(inv, 'produtos', None)
            return inv

        # Qualquer outro caso
        return None
