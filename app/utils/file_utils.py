import hashlib
import os
import magic
from pathlib import Path
from typing import Tuple, Optional
from app.core.logger import logger

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file"""
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read and update hash in chunks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating file hash: {str(e)}")
        return None


class FileValidator:
    """Comprehensive file validation for supported document types"""
    
    def __init__(self):
        self.magic = magic.Magic(mime=True)
        
        # Supported file extensions by category
        self.pdf_extensions = {'.pdf'}
        self.spreadsheet_extensions = {'.xlsx', '.xls', '.csv'}
        self.word_extensions = {'.doc', '.docx'}
        
        # All supported extensions
        self.supported_extensions = (
            self.pdf_extensions | 
            self.spreadsheet_extensions | 
            self.word_extensions
        )
        
        # MIME type mappings for validation
        self.mime_mappings = {
            # PDF
            '.pdf': ['application/pdf'],
            
            # Spreadsheet
            '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
            '.xls': ['application/vnd.ms-excel'],
            '.csv': ['text/csv', 'text/plain', 'application/csv'],
            
            # Word
            '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            '.doc': ['application/msword', 'application/vnd.ms-office']
        }
        
        # Magic byte signatures for additional validation
        self.magic_signatures = {
            # PDF
            b'%PDF': 'pdf',
            
            # Excel/Office formats (ZIP-based for newer formats)
            b'PK\x03\x04': 'office_zip',  # XLSX, DOCX (ZIP format)
            
            # Legacy Office formats
            b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': 'office_legacy',  # DOC, XLS
            
            # CSV (text-based, no specific signature but we'll check content)
        }
    
    def validate_file(self, file_path: str, original_filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Comprehensive file validation
        
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (is_valid, file_type, error_message)
        """
        try:
            # Step 1: Validate file existence
            if not os.path.exists(file_path):
                return False, None, "File does not exist"
            
            # Step 2: Check file size (prevent empty files)
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return False, None, "File is empty"
            
            # Step 3: Extract and validate extension
            extension = Path(original_filename).suffix.lower()
            if not extension:
                return False, None, "File has no extension"
            
            if extension not in self.supported_extensions:
                supported_list = ', '.join(sorted(self.supported_extensions))
                return False, None, f"Unsupported file extension '{extension}'. Supported extensions: {supported_list}"
            
            # Step 4: Determine expected file type from extension
            file_type = self._get_file_type_from_extension(extension)
            
            # Step 5: Validate MIME type
            mime_valid, mime_error = self._validate_mime_type(file_path, extension)
            if not mime_valid:
                return False, None, mime_error
            
            # Step 6: Validate magic bytes/content signature
            signature_valid, signature_error = self._validate_file_signature(file_path, extension, file_type)
            if not signature_valid:
                return False, None, signature_error
            
            # Step 7: Additional format-specific validation
            format_valid, format_error = self._validate_format_specific(file_path, extension, file_type)
            if not format_valid:
                return False, None, format_error
            
            logger.info(f"File validation successful: {original_filename} -> {file_type}")
            return True, file_type, None
            
        except Exception as e:
            error_msg = f"File validation error: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def _get_file_type_from_extension(self, extension: str) -> str:
        """Get file type category from extension"""
        if extension in self.pdf_extensions:
            return 'pdf'
        elif extension in self.spreadsheet_extensions:
            return 'spreadsheet'
        elif extension in self.word_extensions:
            return 'word'
        return 'unknown'
    
    def _validate_mime_type(self, file_path: str, extension: str) -> Tuple[bool, Optional[str]]:
        """Validate MIME type matches expected extension"""
        try:
            detected_mime = self.magic.from_file(file_path)
            expected_mimes = self.mime_mappings.get(extension, [])
            
            # Check if detected MIME type is in expected list
            if any(expected in detected_mime.lower() for expected in [mime.lower() for mime in expected_mimes]):
                return True, None
            
            # Special case for CSV - can have various text MIME types
            if extension == '.csv' and any(text_type in detected_mime.lower() for text_type in ['text', 'csv']):
                return True, None
            
            error_msg = f"MIME type mismatch. Expected one of {expected_mimes} for {extension}, but detected: {detected_mime}"
            return False, error_msg
            
        except Exception as e:
            return False, f"MIME type validation error: {str(e)}"
    
    def _validate_file_signature(self, file_path: str, extension: str, file_type: str) -> Tuple[bool, Optional[str]]:
        """Validate file signature (magic bytes)"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)  # Read first 16 bytes
            
            # PDF validation
            if extension == '.pdf':
                if not header.startswith(b'%PDF'):
                    return False, "Invalid PDF signature. File may be corrupted or not a real PDF."
            
            # Office ZIP-based formats (XLSX, DOCX)
            elif extension in ['.xlsx', '.docx']:
                if not header.startswith(b'PK\x03\x04'):
                    return False, f"Invalid {extension.upper()} signature. File may be corrupted or not a real Office document."
            
            # Legacy Office formats (DOC, XLS)
            elif extension in ['.doc', '.xls']:
                if not header.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
                    return False, f"Invalid {extension.upper()} signature. File may be corrupted or not a real legacy Office document."
            
            # CSV files don't have a specific signature, but we'll validate content structure
            elif extension == '.csv':
                # For CSV, we'll do content validation in format-specific validation
                pass
            
            return True, None
            
        except Exception as e:
            return False, f"File signature validation error: {str(e)}"
    
    def _validate_format_specific(self, file_path: str, extension: str, file_type: str) -> Tuple[bool, Optional[str]]:
        """Additional format-specific validation"""
        try:
            # CSV-specific validation
            if extension == '.csv':
                import pandas as pd
                try:
                    # Try to read first few rows to validate CSV structure
                    df = pd.read_csv(file_path, nrows=5)
                    if len(df.columns) < 1:
                        return False, "CSV file appears to be empty or invalid"
                    return True, None
                except Exception as csv_error:
                    return False, f"Invalid CSV format: {str(csv_error)}"
            
            # For other formats, basic validation is sufficient
            return True, None
            
        except Exception as e:
            return False, f"Format-specific validation error: {str(e)}"
    
    def get_supported_extensions(self) -> list:
        """Get list of all supported extensions"""
        return sorted(list(self.supported_extensions))
    
    def is_supported_extension(self, filename: str) -> bool:
        """Check if filename has a supported extension"""
        extension = Path(filename).suffix.lower()
        return extension in self.supported_extensions


# Create global validator instance
file_validator = FileValidator()


def validate_uploaded_file(file_path: str, original_filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Convenience function for file validation
    
    Returns:
        Tuple[bool, Optional[str], Optional[str]]: (is_valid, file_type, error_message)
    """
    return file_validator.validate_file(file_path, original_filename)


def get_supported_file_extensions() -> list:
    """Get list of supported file extensions"""
    return file_validator.get_supported_extensions()


def is_supported_file(filename: str) -> bool:
    """Check if file has supported extension"""
    return file_validator.is_supported_extension(filename) 