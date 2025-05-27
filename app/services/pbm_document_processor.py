from app.services.classifier_agent import DocumentClassifierAgent
from app.services.pbm_extraction_agent import PBMExtractionAgent
from app.services.pdf_reader import PDFReader
from app.services.spreadsheet_reader import SpreadsheetReader 
from app.services.word_reader import WordReader
from app.core.logger import logger
from typing import Dict, Any
from pathlib import Path
from app.services.pbm_validation_agent import PBMValidationAgent

class PBMDocumentProcessor:
    """Main PBM document processing workflow"""
    
    def __init__(self):
        self.classifier = DocumentClassifierAgent()
        self.extractor = PBMExtractionAgent()
        self.validator = PBMValidationAgent()
        
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process PBM contract document and extract information"""
        
        # Validate file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Classify document
        doc_type = self.classifier.classify(file_path)
        
        # Handle unknown document type
        if doc_type == 'unknown':
            return {
                "error": "Could not determine document type",
                "status": "failed",
                "file_path": file_path
            }
        
        # Select appropriate reader
        reader = self._get_reader(doc_type, file_path)
        if not reader:
            raise ValueError(f"Unsupported document type: {doc_type}")
            
        # Read document
        metadata = reader.get_metadata()
        content = reader.get_full_text() if hasattr(reader, 'get_full_text') else str(reader.get_all_sheets_data())
        
        # Extract information using PBM-specific extraction
        extracted_data = self.extractor.extract(metadata, content)
        
        # Validate extracted data using PBM-specific validation
        validation_status = self.validator.validate(extracted_data)
        
        return {
            "extracted_data": extracted_data,
            "validation_status": validation_status,
            "doc_type": doc_type,
            "contract_type": extracted_data.get("contract_type", "UNKNOWN")
        }
    
    def _get_reader(self, doc_type: str, file_path: str):
        """Get appropriate document reader based on document type"""
        if doc_type == 'pdf':
            reader = PDFReader(file_path)
            reader.open_document()
            return reader
        elif doc_type == 'excel':
            reader = SpreadsheetReader(file_path)
            reader.read_file()
            return reader
        elif doc_type == 'word':
            reader = WordReader(file_path)
            reader.open_document()
            return reader
        return None 