import abc
import xml.etree.ElementTree as ET
from decimal import Decimal
from datetime import date, datetime
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
    def extract(self, file_content: bytes, filename: str) -> InvoiceData:
        raise NotImplementedError

class PDFExtractor(ExtractorInterface):
    def extract(self, file_content: bytes, filename: str) -> InvoiceData:
        print("--- USANDO EXTRATOR PDF ---")
        # Simulação de extração de PDF
        return InvoiceData(
            numero="PDF-001",
            remetente_cnpj="12.345.678/0001-90",
            remetente_nome="Empresa PDF LTDA",
            destinatario_cnpj="99.999.999/0001-99",
            destinatario_nome="Minha Empresa Inc",
            valor_total=Decimal("1500.00"),
            data_emissao=date.today(),
            data_vencimento=date.today()
        )

class XMLExtractor(ExtractorInterface):
    def extract(self, file_content: bytes, filename: str) -> InvoiceData:
        print("--- USANDO EXTRATOR XML (NFe) ---")
        try:
            root = ET.fromstring(file_content.decode('utf-8'))
            # Simulação de parsing XML NFe
            return InvoiceData(
                numero="XML-NFe-001",
                remetente_cnpj="11.111.111/0001-11",
                remetente_nome="Fornecedor XML SA",
                destinatario_cnpj="99.999.999/0001-99",
                destinatario_nome="Minha Empresa Inc",
                valor_total=Decimal("2000.00"),
                data_emissao=date.today(),
                data_vencimento=date.today()
            )
        except ET.ParseError:
            raise ValueError("Arquivo XML inválido")

class ImageExtractor(ExtractorInterface):
    def extract(self, file_content: bytes, filename: str) -> InvoiceData:
        print("--- USANDO EXTRATOR OCR (IMAGEM) ---")
        # Simulação de OCR
        return InvoiceData(
            numero="OCR-001",
            remetente_cnpj="22.222.222/0001-22",
            remetente_nome="Empresa Imagem LTDA",
            destinatario_cnpj="99.999.999/0001-99",
            destinatario_nome="Minha Empresa Inc",
            valor_total=Decimal("800.00"),
            data_emissao=date.today(),
            data_vencimento=date.today()
        )

class ExtractorFactory:
    @staticmethod
    def get_extractor(filename: str) -> ExtractorInterface:
        extension = filename.lower().split('.')[-1]
        
        if extension == 'pdf':
            return PDFExtractor()
        elif extension == 'xml':
            return XMLExtractor()
        elif extension in ['jpg', 'jpeg', 'png', 'tiff']:
            return ImageExtractor()
        else:
            return SimulatedExtractor()

class SimulatedExtractor(ExtractorInterface):
    def extract(self, file_content: bytes, filename: str) -> InvoiceData:
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
