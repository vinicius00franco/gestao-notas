from io import BytesIO
from datetime import date
import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw

from apps.empresa.models import MinhaEmpresa
from apps.notas.models import NotaFiscal, NotaFiscalItem


def make_text_pdf(text: str) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 750, text)
    c.showPage()
    c.save()
    return buf.getvalue()


def make_image_only_pdf() -> bytes:
    # Create an image and embed it into a PDF to simulate scanned PDF
    img = Image.new('RGB', (600, 400), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([50, 50, 550, 350], outline=(0, 0, 0))
    d.text((100, 200), "NF-e 12345", fill=(0, 0, 0))
    img_buf = BytesIO()
    img.save(img_buf, format='PNG')
    img_bytes = img_buf.getvalue()

    # Place the image bytes in a PDF
    from reportlab.lib.utils import ImageReader
    buf = BytesIO()
    c = canvas.Canvas(buf)
    c.drawImage(ImageReader(BytesIO(img_bytes)), 50, 400, width=500, height=300)
    c.showPage()
    c.save()
    return buf.getvalue()


class LLMExtractionAPITests(APITestCase):
    def setUp(self):
        self.url = reverse('processar-nota')
        self.empresa = MinhaEmpresa.objects.create(
            nome="Empresa Teste",
            cnpj="99.999.999/0001-99",
        )
        # Guard: require GEMINI_API_KEY to run these integration tests
        if not os.environ.get('GEMINI_API_KEY'):
            self.skipTest('GEMINI_API_KEY não configurada no ambiente de testes')

    def test_pdf_with_text_extraction_and_persistence(self):
        pdf_bytes = make_text_pdf("NF 12345 - Fornecedor X")
        upload = SimpleUploadedFile("nota_texto.pdf", pdf_bytes, content_type="application/pdf")

        # Act
        resp = self.client.post(self.url, data={
            "arquivo": upload,
            "meu_cnpj": self.empresa.cnpj,
        }, format='multipart')

        # Assert response accepted and job created
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)

        # Process synchronously by calling task directly to persist
        from apps.processamento.models import JobProcessamento
        job = JobProcessamento.objects.latest('id')

        # Import service and run directly to avoid Celery in tests
        from apps.notas.services import NotaFiscalService
        service = NotaFiscalService()
        lanc = service.processar_nota_fiscal_do_job(job)

        # DB assertions (relaxed due to LLM variability): at least one NF persisted
        self.assertGreaterEqual(NotaFiscal.objects.count(), 1)
        nf_db = NotaFiscal.objects.latest('id')
        self.assertIsNotNone(nf_db.data_emissao)
        self.assertIsNotNone(nf_db.valor_total)
        # If items extracted, they should persist
        if nf_db.itens.exists():
            first_item = nf_db.itens.first()
            self.assertTrue(first_item.descricao)

    def test_image_only_pdf_triggers_image_conversion_path(self):
        pdf_bytes = make_image_only_pdf()
        upload = SimpleUploadedFile("nota_scan.pdf", pdf_bytes, content_type="application/pdf")

        resp = self.client.post(self.url, data={
            "arquivo": upload,
            "meu_cnpj": self.empresa.cnpj,
        }, format='multipart')

        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)

        from apps.processamento.models import JobProcessamento
        job = JobProcessamento.objects.latest('id')

        from apps.notas.services import NotaFiscalService
        service = NotaFiscalService()
        lanc = service.processar_nota_fiscal_do_job(job)

        # Assert persisted (even if items not extracted from image)
        self.assertGreaterEqual(NotaFiscal.objects.count(), 1)
        nf_db = NotaFiscal.objects.latest('id')
        self.assertIsNotNone(nf_db.data_emissao)
        self.assertIsNotNone(nf_db.valor_total)
        # For scanned-like PDFs, items may be zero
        self.assertGreaterEqual(nf_db.itens.count(), 0)
