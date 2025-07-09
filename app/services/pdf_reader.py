import PyPDF2
from typing import Dict, Any, Optional, List
from tempfile import TemporaryDirectory
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
from app.models.citation import StructuredContent, SourceLocation, SourceType

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
    
    def get_structured_content(self) -> List[StructuredContent]:
        """Get content with source location tracking"""
        structured_content = []
        
        if not self.pdf_reader:
            return structured_content
        
        if not self.needs_ocr:
            # Use regular PDF text extraction with page tracking
            for page_num, page in enumerate(self.pdf_reader.pages, 1):
                page_text = page.extract_text().strip()
                if page_text:
                    # Split into sections/paragraphs for better granularity
                    sections = self._split_into_sections(page_text)
                    for i, section in enumerate(sections):
                        if section.strip():
                            source_location = SourceLocation(
                                type=SourceType.PAGE,
                                reference=f"page {page_num}",
                                text=section[:200] + "..." if len(section) > 200 else section
                            )
                            structured_content.append(StructuredContent(
                                content=section,
                                source_location=source_location
                            ))
        else:
            # Use OCR with page tracking
            try:
                with TemporaryDirectory() as tempdir:
                    pdf_pages = convert_from_path(self.file_path, 500)
                    
                    for page_enumeration, page in enumerate(pdf_pages, start=1):
                        filename = f"{tempdir}/page_{page_enumeration:03}.jpg"
                        page.save(filename, "JPEG")
                        
                        try:
                            text = str(pytesseract.image_to_string(Image.open(filename)))
                            text = text.replace("-\n", "").strip()
                            
                            if text:
                                sections = self._split_into_sections(text)
                                for section in sections:
                                    if section.strip():
                                        source_location = SourceLocation(
                                            type=SourceType.PAGE,
                                            reference=f"page {page_enumeration}",
                                            text=section[:200] + "..." if len(section) > 200 else section
                                        )
                                        structured_content.append(StructuredContent(
                                            content=section,
                                            source_location=source_location
                                        ))
                        except Exception as e:
                            print(f"OCR error on page {page_enumeration}: {str(e)}")
                            # Fall back to regular PDF extraction
                            if page_enumeration <= len(self.pdf_reader.pages):
                                page_text = self.pdf_reader.pages[page_enumeration-1].extract_text().strip()
                                if page_text:
                                    source_location = SourceLocation(
                                        type=SourceType.PAGE,
                                        reference=f"page {page_enumeration}",
                                        text=page_text[:200] + "..." if len(page_text) > 200 else page_text
                                    )
                                    structured_content.append(StructuredContent(
                                        content=page_text,
                                        source_location=source_location
                                    ))
            except Exception as e:
                print(f"OCR processing error: {str(e)}")
                # Fall back to regular PDF extraction
                for page_num, page in enumerate(self.pdf_reader.pages, 1):
                    page_text = page.extract_text().strip()
                    if page_text:
                        source_location = SourceLocation(
                            type=SourceType.PAGE,
                            reference=f"page {page_num}",
                            text=page_text[:200] + "..." if len(page_text) > 200 else page_text
                        )
                        structured_content.append(StructuredContent(
                            content=page_text,
                            source_location=source_location
                        ))
        
        return structured_content
    
    def _split_into_sections(self, text: str) -> List[str]:
        """Split text into logical sections for better source tracking"""
        # Split by multiple newlines (paragraph breaks)
        sections = re.split(r'\n\s*\n', text)
        
        # Further split very long sections
        final_sections = []
        for section in sections:
            if len(section) > 1000:  # Split long sections
                # Try to split by sentences
                sentences = re.split(r'(?<=[.!?])\s+', section)
                current_section = ""
                for sentence in sentences:
                    if len(current_section + sentence) > 1000 and current_section:
                        final_sections.append(current_section.strip())
                        current_section = sentence
                    else:
                        current_section += " " + sentence if current_section else sentence
                if current_section:
                    final_sections.append(current_section.strip())
            else:
                final_sections.append(section.strip())
        
        return [s for s in final_sections if s.strip()]
    
    def get_content_with_citations(self) -> str:
        """Get full text with embedded citation markers"""
        structured_content = self.get_structured_content()
        content_with_citations = []
        
        for i, content in enumerate(structured_content):
            citation_marker = f"[{content.source_location.reference}]"
            content_with_citations.append(f"{citation_marker} {content.content}")
        
        return "\n\n".join(content_with_citations) 