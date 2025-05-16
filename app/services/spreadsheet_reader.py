import pandas as pd
from typing import Dict, Any, List, Optional
import openpyxl
from datetime import datetime

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