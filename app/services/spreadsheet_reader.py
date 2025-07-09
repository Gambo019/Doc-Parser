import pandas as pd
from typing import Dict, Any, List, Optional
import openpyxl
from datetime import datetime
from app.models.citation import StructuredContent, SourceLocation, SourceType

class SpreadsheetReader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.workbook = None
        self.df = None
        
    def read_file(self) -> bool:
        """Read the spreadsheet file"""
        try:
            if self.file_path.endswith('.csv'):
                self.df = pd.read_csv(self.file_path)
            else:
                self.df = pd.read_excel(self.file_path)
                self.workbook = openpyxl.load_workbook(self.file_path)
            return True
        except Exception as e:
            print(f"Error reading spreadsheet: {str(e)}")
            return False
            
    def get_sheet_names(self) -> List[str]:
        """Get list of sheet names"""
        if self.workbook:
            return self.workbook.sheetnames
        return []
    
    def get_sheet_data(self, sheet_name: str) -> Optional[pd.DataFrame]:
        """Get data from specific sheet"""
        try:
            return pd.read_excel(self.file_path, sheet_name=sheet_name)
        except:
            return None
    
    def get_all_sheets_data(self) -> Dict[str, pd.DataFrame]:
        """Get data from all sheets"""
        if self.file_path.endswith('.csv'):
            return {'Sheet1': self.df} if self.df is not None else {}
            
        try:
            return pd.read_excel(self.file_path, sheet_name=None)
        except:
            return {}
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get spreadsheet metadata"""
        metadata = {
            'filename': self.file_path.split('/')[-1],
            'file_type': 'csv' if self.file_path.endswith('.csv') else 'excel',
            'last_modified': datetime.fromtimestamp(
                pd.Timestamp(pd.read_excel(self.file_path).index[0]).timestamp()
            ).isoformat() if not self.file_path.endswith('.csv') else None,
            'sheet_count': len(self.get_sheet_names()) if self.workbook else 1,
            'row_count': len(self.df) if self.df is not None else 0,
            'column_count': len(self.df.columns) if self.df is not None else 0
        }
        return metadata
    
    def get_structured_content(self) -> List[StructuredContent]:
        """Get content with source location tracking (sheet and cell-based for spreadsheets)"""
        structured_content = []
        
        all_sheets = self.get_all_sheets_data()
        
        for sheet_name, df in all_sheets.items():
            if df is None or df.empty:
                continue
                
            # Add sheet header information
            sheet_header = f"Sheet: {sheet_name} ({df.shape[0]} rows, {df.shape[1]} columns)"
            source_location = SourceLocation(
                type=SourceType.SECTION,
                reference=f"Sheet {sheet_name}",
                text=sheet_header
            )
            structured_content.append(StructuredContent(
                content=sheet_header,
                source_location=source_location,
                metadata={"sheet_name": sheet_name, "is_header": True}
            ))
            
            # Process column headers
            headers_text = " | ".join([str(col) for col in df.columns])
            if headers_text:
                source_location = SourceLocation(
                    type=SourceType.SHEET_CELL,
                    reference=f"{sheet_name}:Headers",
                    text=headers_text
                )
                structured_content.append(StructuredContent(
                    content=f"Column Headers: {headers_text}",
                    source_location=source_location,
                    metadata={"sheet_name": sheet_name, "is_headers": True}
                ))
            
            # Process each row with cell references
            for row_idx, row in df.iterrows():
                # Create row summary
                row_values = []
                for col_idx, (col_name, value) in enumerate(row.items()):
                    if pd.notna(value) and str(value).strip():
                        cell_ref = self._get_excel_cell_reference(row_idx + 2, col_idx)  # +2 because pandas is 0-indexed and we have headers
                        row_values.append(f"{col_name}: {value}")
                
                if row_values:
                    row_text = " | ".join(row_values)
                    source_location = SourceLocation(
                        type=SourceType.SHEET_CELL,
                        reference=f"{sheet_name}:Row{row_idx + 2}",
                        text=row_text[:200] + "..." if len(row_text) > 200 else row_text
                    )
                    structured_content.append(StructuredContent(
                        content=row_text,
                        source_location=source_location,
                        metadata={
                            "sheet_name": sheet_name, 
                            "row_number": row_idx + 2,
                            "is_data_row": True
                        }
                    ))
                    
                    # For important-looking data, also create individual cell references
                    for col_idx, (col_name, value) in enumerate(row.items()):
                        if pd.notna(value) and str(value).strip() and self._is_important_cell(col_name, value):
                            cell_ref = self._get_excel_cell_reference(row_idx + 2, col_idx)
                            source_location = SourceLocation(
                                type=SourceType.SHEET_CELL,
                                reference=f"{sheet_name}:{cell_ref}",
                                text=f"{col_name}: {value}"
                            )
                            structured_content.append(StructuredContent(
                                content=f"{col_name}: {value}",
                                source_location=source_location,
                                metadata={
                                    "sheet_name": sheet_name,
                                    "cell_reference": cell_ref,
                                    "column_name": col_name,
                                    "is_individual_cell": True
                                }
                            ))
        
        return structured_content
    
    def _get_excel_cell_reference(self, row: int, col: int) -> str:
        """Convert row/column numbers to Excel cell reference (e.g., A1, B2)"""
        col_letter = ""
        while col >= 0:
            col_letter = chr(65 + (col % 26)) + col_letter
            col = col // 26 - 1
            if col < 0:
                break
        return f"{col_letter}{row}"
    
    def _is_important_cell(self, col_name: str, value: Any) -> bool:
        """Determine if a cell contains important information worth individual citation"""
        # Look for key contract terms in column names
        important_keywords = [
            'name', 'customer', 'account', 'id', 'date', 'amount', 'fee', 'term', 
            'rate', 'discount', 'rebate', 'address', 'contact', 'email', 'phone',
            'contract', 'agreement', 'price', 'cost', 'payment', 'billing'
        ]
        
        col_name_lower = str(col_name).lower()
        for keyword in important_keywords:
            if keyword in col_name_lower:
                return True
        
        # Look for numeric values that might be important
        try:
            numeric_value = float(str(value).replace(',', '').replace('$', '').replace('%', ''))
            if numeric_value > 0:  # Any positive number might be important
                return True
        except:
            pass
        
        # Look for date patterns
        date_patterns = ['/', '-', '20', '19']
        value_str = str(value)
        if any(pattern in value_str for pattern in date_patterns) and len(value_str) >= 8:
            return True
            
        return False
    
    def get_content_with_citations(self) -> str:
        """Get full text with embedded citation markers"""
        structured_content = self.get_structured_content()
        content_with_citations = []
        
        current_sheet = None
        for content in structured_content:
            sheet_name = content.metadata.get("sheet_name") if content.metadata else None
            
            # Add sheet separator
            if sheet_name != current_sheet:
                current_sheet = sheet_name
                content_with_citations.append(f"\n=== {sheet_name} ===")
            
            citation_marker = f"[{content.source_location.reference}]"
            content_with_citations.append(f"{citation_marker} {content.content}")
        
        return "\n".join(content_with_citations) 