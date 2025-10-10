"""
Extratores multimodais para PDFs e imagens.
Suporta extração de texto, conversão PDF→imagem e processamento direto de imagens.
"""
import io
from typing import List, Tuple, Optional
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from pdf2image import convert_from_bytes
except ImportError:
    convert_from_bytes = None

try:
    from PIL import Image
except ImportError:
    Image = None


class PDFProcessor:
    """Processa PDFs extraindo texto e convertendo para imagens."""
    
    def __init__(self, max_pages_per_batch: int = 10):
        if PdfReader is None:
            raise ImportError(
                "pypdf não instalado. Instale com: pip install pypdf"
            )
        self.max_pages_per_batch = max_pages_per_batch
    
    def extract_text(self, pdf_bytes: bytes) -> Tuple[str, int]:
        """
        Extrai texto de PDF.
        
        Args:
            pdf_bytes: Bytes do arquivo PDF
            
        Returns:
            Tupla (texto_extraído, num_páginas)
        """
        reader = PdfReader(io.BytesIO(pdf_bytes))
        num_pages = len(reader.pages)
        
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        
        full_text = '\n\n'.join(text_parts)
        return full_text, num_pages
    
    def has_extractable_text(self, pdf_bytes: bytes, min_chars: int = 100) -> bool:
        """
        Verifica se PDF tem texto extraível.
        
        Args:
            pdf_bytes: Bytes do PDF
            min_chars: Mínimo de caracteres para considerar válido
            
        Returns:
            True se tem texto extraível suficiente
        """
        text, _ = self.extract_text(pdf_bytes)
        return len(text.strip()) >= min_chars
    
    def convert_to_images(
        self,
        pdf_bytes: bytes,
        dpi: int = 200,
        fmt: str = 'JPEG'
    ) -> List[bytes]:
        """
        Converte PDF em lista de imagens (uma por página).
        
        Args:
            pdf_bytes: Bytes do PDF
            dpi: Resolução (maior = melhor qualidade, mais pesado)
            fmt: Formato de imagem ('JPEG' ou 'PNG')
            
        Returns:
            Lista de bytes de imagens
        """
        if convert_from_bytes is None:
            raise ImportError(
                "pdf2image não instalado. Instale com: pip install pdf2image\n"
                "Requer também poppler-utils no sistema."
            )
        
        images = convert_from_bytes(pdf_bytes, dpi=dpi)
        
        image_bytes_list = []
        for img in images:
            buf = io.BytesIO()
            img.save(buf, format=fmt, quality=85 if fmt == 'JPEG' else None)
            buf.seek(0)
            image_bytes_list.append(buf.read())
        
        return image_bytes_list
    
    def split_into_batches(
        self,
        pdf_bytes: bytes,
        pages_per_batch: Optional[int] = None
    ) -> List[bytes]:
        """
        Divide PDF em batches menores.
        
        Args:
            pdf_bytes: Bytes do PDF original
            pages_per_batch: Páginas por batch (usa max_pages_per_batch se None)
            
        Returns:
            Lista de PDFs (como bytes), cada um com até pages_per_batch páginas
        """
        batch_size = pages_per_batch or self.max_pages_per_batch
        
        reader = PdfReader(io.BytesIO(pdf_bytes))
        num_pages = len(reader.pages)
        
        if num_pages <= batch_size:
            return [pdf_bytes]  # Não precisa dividir
        
        # Não implementado: divisão de PDF requer PyPDF writer
        # Por simplicidade, converte para imagens e processa em batches
        images = self.convert_to_images(pdf_bytes)
        
        batches = []
        for i in range(0, len(images), batch_size):
            batch_images = images[i:i + batch_size]
            batches.append(batch_images)  # Retorna lista de imagens, não bytes PDF
        
        return batches


class ImageProcessor:
    """Processa imagens para envio ao LLM."""
    
    def __init__(self, max_dimension: int = 2048):
        if Image is None:
            raise ImportError(
                "Pillow não instalado. Instale com: pip install Pillow"
            )
        self.max_dimension = max_dimension
    
    def load_image(self, image_bytes: bytes) -> Image.Image:
        """Carrega imagem a partir de bytes."""
        return Image.open(io.BytesIO(image_bytes))
    
    def resize_if_needed(self, img: Image.Image) -> Image.Image:
        """
        Redimensiona imagem se exceder max_dimension mantendo aspect ratio.
        
        Args:
            img: Imagem PIL
            
        Returns:
            Imagem redimensionada (ou original se não precisar)
        """
        width, height = img.size
        
        if width <= self.max_dimension and height <= self.max_dimension:
            return img
        
        # Calcula nova dimensão mantendo aspect ratio
        if width > height:
            new_width = self.max_dimension
            new_height = int(height * (self.max_dimension / width))
        else:
            new_height = self.max_dimension
            new_width = int(width * (self.max_dimension / height))
        
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def optimize_for_llm(self, image_bytes: bytes) -> bytes:
        """
        Otimiza imagem para envio ao LLM.
        Redimensiona se necessário e converte para JPEG.
        
        Args:
            image_bytes: Bytes da imagem original
            
        Returns:
            Bytes da imagem otimizada
        """
        img = self.load_image(image_bytes)
        
        # Converte para RGB se necessário (remove alpha channel)
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Redimensiona se necessário
        img = self.resize_if_needed(img)
        
        # Salva como JPEG otimizado
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85, optimize=True)
        buf.seek(0)
        
        return buf.read()
    
    def batch_optimize(self, images_bytes: List[bytes]) -> List[bytes]:
        """Otimiza lista de imagens."""
        return [self.optimize_for_llm(img_bytes) for img_bytes in images_bytes]


class MultimodalExtractor:
    """
    Extrator multimodal que decide melhor estratégia:
    - Tenta extrair texto de PDF primeiro
    - Se falhar ou texto insuficiente, converte para imagens
    - Processa imagens diretamente
    """
    
    def __init__(
        self,
        max_pages_per_batch: int = 10,
        max_image_dimension: int = 2048,
        min_text_chars: int = 100,
    ):
        self.pdf_processor = PDFProcessor(max_pages_per_batch)
        self.image_processor = ImageProcessor(max_image_dimension)
        self.min_text_chars = min_text_chars
    
    def extract_from_pdf(
        self,
        pdf_bytes: bytes,
        prefer_text: bool = True
    ) -> Tuple[Optional[str], Optional[List[bytes]], int]:
        """
        Extrai de PDF tentando texto primeiro, depois imagens.
        
        Args:
            pdf_bytes: Bytes do PDF
            prefer_text: Se True, tenta texto primeiro
            
        Returns:
            Tupla (texto_ou_None, imagens_ou_None, num_páginas)
        """
        num_pages = len(PdfReader(io.BytesIO(pdf_bytes)).pages)
        
        if prefer_text:
            text, _ = self.pdf_processor.extract_text(pdf_bytes)
            if len(text.strip()) >= self.min_text_chars:
                return text, None, num_pages
        
        # Fallback: converte para imagens
        images = self.pdf_processor.convert_to_images(pdf_bytes)
        images_optimized = self.image_processor.batch_optimize(images)
        
        return None, images_optimized, num_pages
    
    def extract_from_image(self, image_bytes: bytes) -> bytes:
        """Processa imagem."""
        return self.image_processor.optimize_for_llm(image_bytes)
    
    def process_multiple_files(
        self,
        files: List[Tuple[bytes, str]]  # [(bytes, filename), ...]
    ) -> List[Tuple[Optional[str], Optional[List[bytes]], str]]:
        """
        Processa múltiplos arquivos.
        
        Args:
            files: Lista de (bytes, filename)
            
        Returns:
            Lista de (texto_ou_None, imagens_ou_None, filename)
        """
        results = []
        
        for file_bytes, filename in files:
            ext = Path(filename).suffix.lower()
            
            if ext == '.pdf':
                text, images, _ = self.extract_from_pdf(file_bytes)
                results.append((text, images, filename))
            elif ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                img_optimized = self.extract_from_image(file_bytes)
                results.append((None, [img_optimized], filename))
            else:
                # Formato desconhecido
                results.append((None, None, filename))
        
        return results
