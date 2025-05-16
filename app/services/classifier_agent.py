from pathlib import Path
import magic
import pandas as pd

class DocumentClassifierAgent:
    """Agent for classifying document types"""
    
    def __init__(self):
        self.magic = magic.Magic(mime=True)
        self.pdf_extensions = {'.pdf'}
        self.excel_extensions = {'.xlsx', '.xls', '.csv'}
        self.word_extensions = {'.doc', '.docx'}
    
    def classify(self, file_path: str) -> str:
        """Classify document type"""
        try:
            extension = Path(file_path).suffix.lower()
            mime_type = self.magic.from_file(file_path)
            
            if extension in self.pdf_extensions or 'pdf' in mime_type.lower():
                return 'pdf'
            if extension in self.excel_extensions or self._is_csv(file_path):
                return 'excel'
            if extension in self.word_extensions or 'word' in mime_type.lower():
                return 'word'
            
            return 'unknown'
            
        except Exception as e:
            print(f"Error classifying document: {str(e)}")
            return 'unknown'
    
    def _is_csv(self, file_path: str) -> bool:
        """Check if file is CSV format"""
        try:
            df = pd.read_csv(file_path, nrows=5)
            return len(df.columns) >= 2
        except:
            return False 