import abc
from apps.classificadores.models import get_classifier

class TipoLancamentoStrategy(abc.ABC):
    @abc.abstractmethod
    def aplica(self, dados_extraidos, minha_empresa) -> dict | None:
        pass

class NotaCompraStrategy(TipoLancamentoStrategy):
    def aplica(self, dados_extraidos, minha_empresa) -> dict | None:
        if dados_extraidos.destinatario_cnpj == minha_empresa.cnpj:
            return {
                'tipo_lancamento': get_classifier('TIPO_LANCAMENTO', 'PAGAR'),
                'parceiro_data': {
                    'cnpj': dados_extraidos.remetente_cnpj,
                    'nome': dados_extraidos.remetente_nome,
                    'clf_tipo': get_classifier('TIPO_PARCEIRO', 'FORNECEDOR')
                }
            }
        return None

class NotaVendaStrategy(TipoLancamentoStrategy):
    def aplica(self, dados_extraidos, minha_empresa) -> dict | None:
        if dados_extraidos.remetente_cnpj == minha_empresa.cnpj:
            return {
                'tipo_lancamento': get_classifier('TIPO_LANCAMENTO', 'RECEBER'),
                'parceiro_data': {
                    'cnpj': dados_extraidos.destinatario_cnpj,
                    'nome': dados_extraidos.destinatario_nome,
                    'clf_tipo': get_classifier('TIPO_PARCEIRO', 'CLIENTE')
                }
            }
        return None

class TipoLancamentoContext:
    def __init__(self):
        self.strategies = [NotaCompraStrategy(), NotaVendaStrategy()]
    
    def determinar_tipo_e_parceiro(self, dados_extraidos, minha_empresa):
        for strategy in self.strategies:
            resultado = strategy.aplica(dados_extraidos, minha_empresa)
            if resultado:
                return resultado
        raise ValueError("Não foi possível determinar o tipo de lançamento para a nota fiscal.")