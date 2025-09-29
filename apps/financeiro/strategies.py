# apps/financeiro/strategies.py
import abc
from apps.classificadores.models import get_classifier

class TipoLancamentoStrategy(abc.ABC):
    @abc.abstractmethod
    def determinar_tipo_e_parceiro(self, dados_extraidos, minha_empresa):
        pass

class NotaCompraStrategy(TipoLancamentoStrategy):
    def determinar_tipo_e_parceiro(self, dados_extraidos, minha_empresa):
        if dados_extraidos.destinatario_cnpj == minha_empresa.cnpj:
            return {
                'tipo_lancamento': get_classifier('TIPO_LANCAMENTO', 'PAGAR'),
                'parceiro_data': {
                    'cnpj': dados_extraidos.remetente_cnpj,
                    'nome': dados_extraidos.remetente_nome,
                    'clf_tipo': get_classifier('TIPO_PARCEIRO', 'FORNECEDOR')
                }
            }
        raise ValueError("Nota não é de compra para esta empresa")

class NotaVendaStrategy(TipoLancamentoStrategy):
    def determinar_tipo_e_parceiro(self, dados_extraidos, minha_empresa):
        if dados_extraidos.remetente_cnpj == minha_empresa.cnpj:
            return {
                'tipo_lancamento': get_classifier('TIPO_LANCAMENTO', 'RECEBER'),
                'parceiro_data': {
                    'cnpj': dados_extraidos.destinatario_cnpj,
                    'nome': dados_extraidos.destinatario_nome,
                    'clf_tipo': get_classifier('TIPO_PARCEIRO', 'CLIENTE')
                }
            }
        raise ValueError("Nota não é de venda desta empresa")

class TipoLancamentoContext:
    def __init__(self):
        self.strategies = [NotaCompraStrategy(), NotaVendaStrategy()]
    
    def determinar_tipo_e_parceiro(self, dados_extraidos, minha_empresa):
        for strategy in self.strategies:
            try:
                return strategy.determinar_tipo_e_parceiro(dados_extraidos, minha_empresa)
            except ValueError:
                continue
        raise ValueError("Nota fiscal não pertence à sua empresa (CNPJ não corresponde).")