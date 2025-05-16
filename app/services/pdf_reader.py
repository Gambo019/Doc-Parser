import PyPDF2
from typing import Dict, Any, Optional, List
from tempfile import TemporaryDirectory
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

class PDFReader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.pdf_reader = None
        self.needs_ocr = True
        
    def open_document(self) -> bool:
        """Open the PDF file and create a reader object"""
        try:
            file = open(self.file_path, 'rb')
            self.pdf_reader = PyPDF2.PdfReader(file)
            
            # Check if PDF needs OCR by attempting to extract text from first page
            first_page_text = self.pdf_reader.pages[0].extract_text().strip()
            if not first_page_text:
                # If no text found, mark for OCR processing
                self.needs_ocr = True
            else:
                self.needs_ocr = False
            return True
        except FileNotFoundError:
            print(f"Error: The file '{self.file_path}' was not found.")
            return False
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False
    
    def get_page_count(self) -> int:
        """Return the total number of pages"""
        if self.pdf_reader:
            return len(self.pdf_reader.pages)
        return 0
    
    def read_page(self, page_num: int) -> Optional[str]:
        """Read a specific page"""
        if self.pdf_reader and 0 <= page_num < self.get_page_count():
            return self.pdf_reader.pages[page_num].extract_text()
        return None
    
    def get_full_text(self) -> str:
        """Get full text content of the PDF"""
        if not self.pdf_reader:
            return ""
        
        if not self.needs_ocr:
            # Use regular PDF text extraction
            text = []
            for page in self.pdf_reader.pages:
                text.append(page.extract_text())
            return "\n".join(text)
        else:
            # Use OCR for scanned documents
            return self._extract_text_with_ocr()
    
    def _extract_text_with_ocr(self) -> str:
        """Extract text using OCR for scanned documents"""
        try:
            extracted_text = ""
            
            with TemporaryDirectory() as tempdir:
                # Convert PDF to images
                pdf_pages = convert_from_path(self.file_path, 500)
                
                # Process each page
                for page_enumeration, page in enumerate(pdf_pages, start=1):
                    # Save page as temporary image
                    filename = f"{tempdir}/page_{page_enumeration:03}.jpg"
                    page.save(filename, "JPEG")
                    
                    try:
                        # Extract text from image
                        text = str(pytesseract.image_to_string(Image.open(filename)))
                        text = text.replace("-\n", "")
                        extracted_text += text + "\n"
                    except Exception as e:
                        print(f"OCR error on page {page_enumeration}: {str(e)}")
                        # Fall back to regular PDF extraction for this page
                        if self.pdf_reader and page_enumeration <= len(self.pdf_reader.pages):
                            extracted_text += self.pdf_reader.pages[page_enumeration-1].extract_text() + "\n"
            
            return extracted_text
        except Exception as e:
            print(f"OCR processing error: {str(e)}")
            # Fall back to regular PDF extraction
            if self.pdf_reader:
                return "\n".join(page.extract_text() for page in self.pdf_reader.pages)
            return ""
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get PDF metadata"""
        if self.pdf_reader:
            return dict(self.pdf_reader.metadata)
        return {} 