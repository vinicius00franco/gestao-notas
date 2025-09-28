import abc
from decimal import Decimal
from datetime import date
from pydantic import BaseModel

class InvoiceData(BaseModel):
    numero: str
    remetente_cnpj: str
    remetente_nome: str
    destinatario_cnpj: str
    destinatario_nome: str
    valor_total: Decimal
    data_emissao: date
    data_vencimento: date

class ExtractorInterface(abc.ABC):
    @abc.abstractmethod
    def extract(self, file_content: bytes, filename: str):
        raise NotImplementedError

class SimulatedExtractor(ExtractorInterface):
    def extract(self, file_content: bytes, filename: str):
        print("--- USANDO EXTRATOR SIMULADO ---")
        is_compra = "compra" in filename.lower()
        my_cnpj = "99.999.999/0001-99"
        if is_compra:
            return InvoiceData(
                remetente_cnpj="11.222.333/0001-44", remetente_nome="Fornecedor Simulado LTDA",
                destinatario_cnpj=my_cnpj, destinatario_nome="Minha Empresa Inc",
                valor_total=Decimal("750.00"), data_emissao=date(2025, 9, 26),
                data_vencimento=date(2025, 10, 26), numero="NF-COMPRA-123"
            )
        else:
            return InvoiceData(
                remetente_cnpj=my_cnpj, remetente_nome="Minha Empresa Inc",
                destinatario_cnpj="55.666.777/0001-88", destinatario_nome="Cliente Simulado SA",
                valor_total=Decimal("1200.50"), data_emissao=date(2025, 9, 27),
                data_vencimento=date(2025, 10, 27), numero="NF-VENDA-456"
            )
