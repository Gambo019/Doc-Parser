from app.services.classifier_agent import DocumentClassifierAgent
from app.services.extraction_agent import ExtractionAgent
from app.services.pdf_reader import PDFReader
from app.services.spreadsheet_reader import SpreadsheetReader 
from app.services.word_reader import WordReader
from app.core.logger import logger
from typing import Dict, Any
from pathlib import Path
from app.services.validation_agent import ValidationAgent

class DocumentProcessor:
    """Main document processing workflow"""
    
    def __init__(self):
        self.classifier = DocumentClassifierAgent()
        self.extractor = ExtractionAgent()
        self.validator = ValidationAgent()
        
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process document and extract information"""
        
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
        
        # Extract information
        extracted_data = self.extractor.extract(metadata, content)
        
        # Validate extracted data
        validation_status = self.validator.validate(extracted_data)
        
        return {
            "extracted_data": extracted_data,
            "validation_status": validation_status,
            "doc_type": doc_type
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

# def main():
#     processor = DocumentProcessor()
#     result = processor.process_document("./sample/Exactus_HTO_Cannabinoid_Supply_Agreement_2020.pdf")
#     import pprint
#     pprint.pprint(result)

# if __name__ == "__main__":
#     main() 