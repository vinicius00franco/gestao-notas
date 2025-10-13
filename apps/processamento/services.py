import hashlib
import logging
from .models import JobProcessamento
from .publishers import CeleryTaskPublisher
from .repositories import JobProcessamentoRepository
from apps.empresa.models import MinhaEmpresa
from apps.classificadores.models import get_classifier
from apps.notas.strategies.factory import ExtractionStrategyFactory
from apps.parceiros.models import Parceiro
from apps.notas.models import NotaFiscal
from django.db.models.functions import Replace

logger = logging.getLogger(__name__)

def calcular_hash_arquivo(arquivo):
    """
    Calcula o hash SHA-256 de um arquivo.
    """
    sha256_hash = hashlib.sha256()
    # Garante que o ponteiro do arquivo esteja no início
    arquivo.seek(0)
    for chunk in iter(lambda: arquivo.read(4096), b""):
        sha256_hash.update(chunk)
    # Retorna o ponteiro do arquivo para o início para que ele possa ser lido novamente
    arquivo.seek(0)
    return sha256_hash.hexdigest()

def cnpj_para_numero(cnpj_str):
    """Converte CNPJ string para número inteiro."""
    if not cnpj_str:
        return None
    # Remove pontos, barras e traços
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj_str))
    return int(cnpj_limpo) if cnpj_limpo else None

class ProcessamentoService:
    def criar_job_processamento(self, cnpj: str = None, arquivo=None) -> JobProcessamento:
        logger.info(f"PROCESSAMENTO: Iniciando criação de job - CNPJ: {cnpj}, Arquivo: {arquivo.name if arquivo else 'None'}")

        empresa = None
        if cnpj:
            logger.debug(f"PROCESSAMENTO: Buscando empresa por CNPJ: {cnpj}")
            cnpj_numero = cnpj_para_numero(cnpj)
            logger.debug(f"PROCESSAMENTO: CNPJ convertido: {cnpj_numero}")
            if cnpj_numero:
                try:
                    empresa = MinhaEmpresa.get_by_cnpj(cnpj_numero)
                    logger.info(f"PROCESSAMENTO: Empresa encontrada: {empresa.nome} (ID: {empresa.pk})")
                except MinhaEmpresa.DoesNotExist:
                    logger.warning(f"PROCESSAMENTO: Empresa com CNPJ {cnpj} não encontrada")
                    # CNPJ fornecido mas empresa não existe - erro
                    raise ValueError("Empresa com CNPJ informado não encontrada")
            else:
                logger.warning(f"PROCESSAMENTO: CNPJ inválido: {cnpj}")
        else:
            logger.info("PROCESSAMENTO: Nenhum CNPJ fornecido - processamento sem empresa associada")

        logger.debug("PROCESSAMENTO: Calculando hash do arquivo")
        hash_arquivo = calcular_hash_arquivo(arquivo)
        logger.debug(f"PROCESSAMENTO: Hash calculado: {hash_arquivo}")

        # Preflight: tentar extrair número da nota e CNPJ do parceiro para validar
        # duplicidade antes de criar o job e enfileirar processamento.
        try:
            logger.debug("PROCESSAMENTO: Executando extração rápida para validação de duplicidade")
            # Ler conteúdo do arquivo sem consumir o ponteiro permanentemente
            arquivo.seek(0)
            file_bytes = arquivo.read()
            arquivo.seek(0)

            # Escolher estratégia sugerida pela extensão do arquivo
            suggested_method = ExtractionStrategyFactory.get_strategy_for_file(arquivo.name)
            strategy = ExtractionStrategyFactory.create_strategy(suggested_method)
            extracted = strategy.extract(file_bytes, arquivo.name)

            numero_extraido = getattr(extracted, 'numero', None)
            remetente_cnpj = getattr(extracted, 'remetente_cnpj', None)
            destinatario_cnpj = getattr(extracted, 'destinatario_cnpj', None)

            logger.debug(f"PROCESSAMENTO: Dados extraídos (pré): numero={numero_extraido}, remetente={remetente_cnpj}, destinatario={destinatario_cnpj}")

            parceiro_cnpj_para_validar = None
            # Se o usuário forneceu o CNPJ da sua empresa, o parceiro é o outro CNPJ extraído
            if cnpj:
                cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
                if remetente_cnpj and ''.join(filter(str.isdigit, remetente_cnpj)) == cnpj_limpo:
                    parceiro_cnpj_para_validar = destinatario_cnpj
                elif destinatario_cnpj and ''.join(filter(str.isdigit, destinatario_cnpj)) == cnpj_limpo:
                    parceiro_cnpj_para_validar = remetente_cnpj
                else:
                    # Não conseguimos identificar parceiro com base no meu_cnpj; prefer remete
                    parceiro_cnpj_para_validar = remetente_cnpj or destinatario_cnpj
            else:
                # Sem meu_cnpj, preferir remetente como parceiro (conservador)
                parceiro_cnpj_para_validar = remetente_cnpj or destinatario_cnpj

            if numero_extraido and parceiro_cnpj_para_validar:
                # Normalize digits-only for CNPJ and invoice number
                parceiro_digits = ''.join(filter(str.isdigit, parceiro_cnpj_para_validar))
                numero_digits = ''.join(filter(str.isdigit, str(numero_extraido)))

                # Try to find parceiro by digits-only CNPJ using Replace annotations
                parceiro = (
                    Parceiro.objects
                    .annotate(cnpj_digits=Replace(Replace(Replace('cnpj', '.', ''), '/', ''), '-', ''))
                    .filter(cnpj_digits=parceiro_digits)
                    .first()
                )

                if parceiro:
                    # Normalize nota.numero in DB and compare digits-only
                    exists = (
                        NotaFiscal.objects
                        .annotate(numero_digits=Replace(Replace(Replace('numero', '.', ''), '/', ''), '-', ''))
                        .filter(parceiro=parceiro, numero_digits=numero_digits, chave_acesso__isnull=True)
                        .exists()
                    )

                    if exists:
                        logger.warning(
                            f"PROCESSAMENTO: Nota fiscal já existe para parceiro {parceiro.cnpj} e numero {numero_extraido}"
                        )
                        raise ValueError(f"Nota fiscal já existe: parceiro={parceiro.cnpj}, numero={numero_extraido}")
                else:
                    logger.debug("PROCESSAMENTO: Parceiro extraído não encontrado no cadastro; não validar duplicidade por parceiro")
        except ValueError:
            # Propagar ValueError para ser tratado pela view (400)
            raise
        except Exception:
            # Qualquer falha na extração prévia não deve impedir o fluxo; log e continuar
            logger.exception("PROCESSAMENTO: Falha na extração prévia para validação de duplicidade - ignorando validação")

        job_existente = JobProcessamentoRepository.find_by_hash(hash_arquivo)
        if job_existente:
            logger.info(f"PROCESSAMENTO: Job existente encontrado (ID: {job_existente.id}) - reutilizando arquivo")
            arquivo_a_salvar = job_existente.arquivo_original
        else:
            logger.info("PROCESSAMENTO: Novo arquivo - será salvo")
            arquivo_a_salvar = arquivo

        status_pendente = get_classifier('STATUS_JOB', 'PENDENTE')
        logger.debug(f"PROCESSAMENTO: Status pendente: {status_pendente}")

        job = JobProcessamentoRepository.create_job(
            arquivo_original=arquivo_a_salvar,
            hash_arquivo=hash_arquivo,
            empresa=empresa,
            status=status_pendente,
        )
        logger.info(f"PROCESSAMENTO: Job criado com sucesso - UUID: {job.uuid}, ID: {job.id}")

        logger.debug(f"PROCESSAMENTO: Publicando tarefa Celery para job {job.id}")
        CeleryTaskPublisher().publish_processamento_nota(job_id=job.id)
        logger.info(f"PROCESSAMENTO: Tarefa Celery publicada para job {job.id}")

        return job