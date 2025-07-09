from app.services.classifier_agent import DocumentClassifierAgent
from app.services.pbm_extraction_agent import PBMExtractionAgent
from app.services.pbm_extraction_agent_with_citations import PBMExtractionAgentWithCitations
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
        self.extractor = PBMExtractionAgentWithCitations()  # Citations are now mandatory
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
        
        # Use structured content for citation tracking (mandatory)
        structured_content = reader.get_structured_content() if hasattr(reader, 'get_structured_content') else []
        if not structured_content:
            # Citations are mandatory, so we cannot process documents without structured content
            raise ValueError(f"Structured content required for citations but not available for document type: {doc_type}")
        
        # Extract information with citations using PBM-specific extraction (mandatory)
        extraction_result = self.extractor.extract(metadata, structured_content)
        extracted_data = extraction_result.get("extracted_data", {})
        
        # Validate extracted data using PBM-specific validation
        validation_status = self.validator.validate(extracted_data)
        
        # Prepare return object with mandatory citations
        result = {
            "extracted_data": extracted_data,
            "validation_status": validation_status,
            "doc_type": doc_type,
            "contract_type": extracted_data.get("ContractType", "UNKNOWN"),
            "citations": extraction_result.get("citations", {}),
            "source_summary": extraction_result.get("source_summary", {}),
            "citation_validation": extraction_result.get("validation_status", {})
        }
        
        return result
    
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