import io
import os
from datetime import date
from decimal import Decimal
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from apps.empresa.models import MinhaEmpresa
from apps.classificadores.models import get_classifier
from apps.processamento.models import JobProcessamento
from apps.notas.services import NotaFiscalService


class Command(BaseCommand):
    help = "Gera uma imagem e um PDF simulando uma nota fiscal, cria Jobs e processa com o service (LLM/fallback)."

    def add_arguments(self, parser):
        parser.add_argument('--cnpj', type=str, default='99.999.999/0001-99', help='CNPJ da MinhaEmpresa')
        parser.add_argument('--dest', type=str, default='media/notas_fiscais_uploads', help='Diretório para salvar arquivos gerados')

    def handle(self, *args, **options):
        dest_dir = options['dest']
        os.makedirs(dest_dir, exist_ok=True)

        with transaction.atomic():
            emp = self._get_or_create_minha_empresa(options['cnpj'])
            status_job = get_classifier('STATUS_JOB', 'CRIADO')

            # 1) Gerar imagem PNG simulando uma NFe
            img_bytes, img_name = self._gerar_imagem_nfe(dest_dir)
            job_img = JobProcessamento.objects.create(
                arquivo_original=ContentFile(img_bytes, name=img_name),
                empresa=emp,
                status=status_job,
            )

            # 2) Gerar PDF simulando uma NFe com itens
            pdf_bytes, pdf_name = self._gerar_pdf_nfe(dest_dir)
            job_pdf = JobProcessamento.objects.create(
                arquivo_original=ContentFile(pdf_bytes, name=pdf_name),
                empresa=emp,
                status=status_job,
            )

            # Processa com service (LLM primeiro, fallback se necessário)
            service = NotaFiscalService()
            lanc_img = service.processar_nota_fiscal_do_job(job_img)
            lanc_pdf = service.processar_nota_fiscal_do_job(job_pdf)

            self.stdout.write(self.style.SUCCESS(
                f"Processados com sucesso: lanc_img={lanc_img.id}, lanc_pdf={lanc_pdf.id}"
            ))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_or_create_minha_empresa(self, cnpj: str) -> MinhaEmpresa:
        emp, _ = MinhaEmpresa.objects.get_or_create(cnpj=cnpj, defaults={'nome': 'Minha Empresa Inc'})
        return emp

    def _gerar_imagem_nfe(self, dest_dir: str):
        """Cria uma imagem PNG simulando uma NFe simples."""
        img = Image.new('RGB', (1240, 1754), color='white')  # A4 @150dpi approx
        d = ImageDraw.Draw(img)

        title = "NOTA FISCAL ELETRÔNICA (NFe)"
        d.text((50, 50), title, fill='black')

        # Dados emitente/destinatário simulados
        linhas = [
            "Emitente: Empresa PDF LTDA - CNPJ: 12.345.678/0001-90",
            "Destinatário: Minha Empresa Inc - CNPJ: 99.999.999/0001-99",
            f"Data Emissão: {date.today().isoformat()}",
            "Chave de Acesso: 12345678901234567890123456789012345678901234",
            "Produtos:",
            "  1) PRODUTO A - Qtd: 2  Vlr Unit: 100,00  Vlr Total: 200,00",
            "  2) PRODUTO B - Qtd: 3  Vlr Unit: 150,00  Vlr Total: 450,00",
            "Valor Total da Nota: 650,00",
        ]

        y = 120
        for linha in linhas:
            d.text((50, y), linha, fill='black')
            y += 40

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        img_bytes = buf.read()

        img_name = 'nfe_simulada.png'
        with open(os.path.join(dest_dir, img_name), 'wb') as f:
            f.write(img_bytes)

        return img_bytes, img_name

    def _gerar_pdf_nfe(self, dest_dir: str):
        """Cria um PDF simples simulando uma NFe com 2 itens."""
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        width, height = A4

        y = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "NOTA FISCAL ELETRÔNICA (NFe)")
        y -= 30

        c.setFont("Helvetica", 11)
        linhas = [
            "Emitente: Fornecedor XYZ SA - CNPJ: 11.222.333/0001-44",
            "Destinatário: Minha Empresa Inc - CNPJ: 99.999.999/0001-99",
            f"Data Emissão: {date.today().isoformat()}",
            "Chave de Acesso: 98765432109876543210987654321098765432109876",
            "Produtos:",
            "  1) PRODUTO X - Qtd: 1  Vlr Unit: 250,00  Vlr Total: 250,00",
            "  2) PRODUTO Y - Qtd: 2  Vlr Unit: 300,00  Vlr Total: 600,00",
            "Valor Total da Nota: 850,00",
        ]

        for linha in linhas:
            c.drawString(40, y, linha)
            y -= 20

        c.showPage()
        c.save()

        buf.seek(0)
        pdf_bytes = buf.read()

        pdf_name = 'nfe_simulada.pdf'
        with open(os.path.join(dest_dir, pdf_name), 'wb') as f:
            f.write(pdf_bytes)

        return pdf_bytes, pdf_name
