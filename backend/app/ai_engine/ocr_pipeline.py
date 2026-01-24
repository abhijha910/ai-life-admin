"""OCR pipeline for document text extraction"""
import pytesseract
from PIL import Image
import PyPDF2
import pdfplumber
from io import BytesIO
from typing import Optional, Tuple
import structlog

logger = structlog.get_logger()


class OCRPipeline:
    """OCR pipeline for extracting text from documents"""
    
    def extract_text(self, file_content: bytes, file_type: str, mime_type: str) -> Tuple[str, bool]:
        """Extract text from document
        
        Returns:
            Tuple of (extracted_text, success)
        """
        try:
            if file_type.lower() in ['pdf'] or 'pdf' in mime_type.lower():
                return self._extract_from_pdf(file_content)
            elif file_type.lower() in ['jpg', 'jpeg', 'png', 'gif', 'bmp'] or 'image' in mime_type.lower():
                return self._extract_from_image(file_content)
            elif file_type.lower() in ['txt']:
                return file_content.decode('utf-8', errors='ignore'), True
            else:
                logger.warning("Unsupported file type for OCR", file_type=file_type)
                return "", False
        except Exception as e:
            logger.error("OCR extraction error", error=str(e))
            return "", False
    
    def _extract_from_pdf(self, file_content: bytes) -> Tuple[str, bool]:
        """Extract text from PDF"""
        try:
            # Try pdfplumber first (better for text-based PDFs)
            try:
                with pdfplumber.open(BytesIO(file_content)) as pdf:
                    text_parts = []
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    if text_parts:
                        return "\n\n".join(text_parts), True
            except Exception:
                pass
            
            # Fallback to PyPDF2
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_parts = []
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            if text_parts:
                return "\n\n".join(text_parts), True
            
            # If no text found, try OCR on first page as image
            logger.info("PDF has no extractable text, trying OCR on first page")
            return self._ocr_pdf_page(file_content, 0)
            
        except Exception as e:
            logger.error("PDF extraction error", error=str(e))
            return "", False
    
    def _extract_from_image(self, file_content: bytes) -> Tuple[str, bool]:
        """Extract text from image using Tesseract OCR"""
        try:
            image = Image.open(BytesIO(file_content))
            
            # Preprocess image for better OCR
            image = self._preprocess_image(image)
            
            # Extract text
            text = pytesseract.image_to_string(image, lang='eng')
            return text.strip(), True
        except Exception as e:
            logger.error("Image OCR error", error=str(e))
            return "", False
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results"""
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # You can add more preprocessing here:
        # - Resize if too small/large
        # - Enhance contrast
        # - Denoise
        # - Deskew
        
        return image
    
    def _ocr_pdf_page(self, pdf_content: bytes, page_num: int) -> Tuple[str, bool]:
        """OCR a specific PDF page as image"""
        try:
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(pdf_content, first_page=page_num+1, last_page=page_num+1)
            if images:
                text = pytesseract.image_to_string(images[0], lang='eng')
                return text.strip(), True
        except Exception as e:
            logger.warning("PDF page OCR error", error=str(e))
        
        return "", False


# Global OCR pipeline instance
ocr_pipeline = OCRPipeline()
