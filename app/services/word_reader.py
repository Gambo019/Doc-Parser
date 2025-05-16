from docx import Document
from typing import Dict, Any, List, Optional
import os
from datetime import datetime

class WordReader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.document = None
        
    def open_document(self) -> bool:
        """Open the Word document"""
        try:
            self.document = Document(self.file_path)
            return True
        except Exception as e:
            print(f"Error opening Word document: {str(e)}")
            return False
    
    def get_full_text(self) -> str:
        """Get full text content of the document"""
        if not self.document:
            return ""
            
        paragraphs = []
        for paragraph in self.document.paragraphs:
            if paragraph.text.strip():
                paragraphs.append(paragraph.text)
                
        return "\n".join(paragraphs)
    
    def get_tables(self) -> List[List[List[str]]]:
        """Get all tables from the document"""
        if not self.document:
            return []
            
        tables = []
        for table in self.document.tables:
            table_data = []
            for row in table.rows:
                row_data = [cell.text for cell in row.cells]
                table_data.append(row_data)
            tables.append(table_data)
        return tables
    
    def get_headers_footers(self) -> Dict[str, str]:
        """Get headers and footers"""
        if not self.document:
            return {}
            
        headers = []
        footers = []
        
        for section in self.document.sections:
            if section.header.text.strip():
                headers.append(section.header.text)
            if section.footer.text.strip():
                footers.append(section.footer.text)
                
        return {
            'headers': headers,
            'footers': footers
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get document metadata"""
        if not self.document:
            return {}
            
        core_properties = self.document.core_properties
        
        metadata = {
            'author': core_properties.author,
            'created': core_properties.created.isoformat() if core_properties.created else None,
            'modified': core_properties.modified.isoformat() if core_properties.modified else None,
            'last_modified_by': core_properties.last_modified_by,
            'title': core_properties.title,
            'subject': core_properties.subject,
            'keywords': core_properties.keywords,
            'category': core_properties.category,
            'comments': core_properties.comments,
            'file_size': os.path.getsize(self.file_path),
            'paragraph_count': len(self.document.paragraphs),
            'table_count': len(self.document.tables)
        }
        
        return {k: v for k, v in metadata.items() if v is not None} 