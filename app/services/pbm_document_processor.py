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
    
    def __init__(self, enable_citations: bool = True):
        self.classifier = DocumentClassifierAgent()
        self.extractor = PBMExtractionAgentWithCitations() if enable_citations else PBMExtractionAgent()
        self.validator = PBMValidationAgent()
        self.enable_citations = enable_citations
        
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
        
        if self.enable_citations:
            # Use structured content for citation tracking
            structured_content = reader.get_structured_content() if hasattr(reader, 'get_structured_content') else []
            if not structured_content:
                # Fallback to regular content if structured content is not available
                content = reader.get_full_text() if hasattr(reader, 'get_full_text') else str(reader.get_all_sheets_data())
                # Use regular extractor as fallback
                extractor = PBMExtractionAgent()
                extracted_result = extractor.extract(metadata, content)
                return {
                    "extracted_data": extracted_result,
                    "validation_status": self.validator.validate(extracted_result),
                    "doc_type": doc_type,
                    "contract_type": extracted_result.get("ContractType", "UNKNOWN"),
                    "citations": None,
                    "citation_error": "Structured content not available for this document type"
                }
            
            # Extract information with citations using PBM-specific extraction
            extraction_result = self.extractor.extract(metadata, structured_content)
            extracted_data = extraction_result.get("extracted_data", {})
            
        else:
            # Use regular extraction without citations
            content = reader.get_full_text() if hasattr(reader, 'get_full_text') else str(reader.get_all_sheets_data())
            extracted_data = self.extractor.extract(metadata, content)
            extraction_result = {"extracted_data": extracted_data}
        
        # Validate extracted data using PBM-specific validation
        validation_status = self.validator.validate(extracted_data)
        
        # Prepare return object
        result = {
            "extracted_data": extracted_data,
            "validation_status": validation_status,
            "doc_type": doc_type,
            "contract_type": extracted_data.get("ContractType", "UNKNOWN")
        }
        
        # Add citation information if enabled
        if self.enable_citations and "citations" in extraction_result:
            result["citations"] = extraction_result["citations"]
            result["source_summary"] = extraction_result.get("source_summary", {})
            result["citation_validation"] = extraction_result.get("validation_status", {})
        
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