from typing import Dict, Any, List, Optional
from pydantic import ValidationError
from datetime import datetime
from app.models.document import DocumentValidation
from app.core.logger import logger

class ValidationAgent:
    """Agent for validating extracted document information"""
    
    def __init__(self):
        self.validation_rules = {
            'date_fields': ['TermStartDate', 'RenewalDate', 'DateSigned'],
            'numeric_fields': ['CommitmentFee', 'SavingsPlanCredit', 'NetPayableFee'],
            'email_fields': ['EmailInvoiceTo']
        }
    
    def validate(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted data against rules and return validation results"""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'validated_data': None
        }
        
        try:
            # Check for required CustomerName
            if not extracted_data.get('CustomerName'):
                validation_results['is_valid'] = False
                validation_results['errors'].append("CustomerName is required")
                return validation_results

            # Basic Pydantic model validation
            validated_data = DocumentValidation(**extracted_data)
            
            # Custom validation rules
            self._validate_dates(validated_data, validation_results)
            self._validate_numeric_values(validated_data, validation_results)
            self._validate_email_format(validated_data, validation_results)
            self._validate_business_rules(validated_data, validation_results)
            
            validation_results['validated_data'] = validated_data.model_dump()
            
        except ValidationError as e:
            validation_results['is_valid'] = False
            validation_results['errors'].extend([str(err) for err in e.errors()])
            logger.error(f"Validation error: {str(e)}")
            
        except Exception as e:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Unexpected validation error: {str(e)}")
            logger.error(f"Unexpected validation error: {str(e)}")
            
        return validation_results
    
    def _validate_dates(self, data: DocumentValidation, results: Dict[str, Any]):
        """Validate date fields"""
        current_date = datetime.now().replace(tzinfo=None)  # Strip timezone info
        
        for field in self.validation_rules['date_fields']:
            date_value = getattr(data, field, None)
            if date_value:
                # Convert to naive datetime for comparison
                if date_value.tzinfo:
                    date_value = date_value.replace(tzinfo=None)
                if date_value > current_date and field != 'RenewalDate':
                    results['warnings'].append(f"{field} is in the future")
                        
    def _validate_numeric_values(self, data: DocumentValidation, results: Dict[str, Any]):
        """Validate numeric fields"""
        for field in self.validation_rules['numeric_fields']:
            value = getattr(data, field, None)
            if value is not None and value < 0:
                results['warnings'].append(f"{field} is negative")
    
    def _validate_email_format(self, data: DocumentValidation, results: Dict[str, Any]):
        """Validate email format"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for field in self.validation_rules['email_fields']:
            email = getattr(data, field, None)
            if email and not re.match(email_pattern, email):
                results['warnings'].append(f"Invalid email format in {field}")
    
    def _validate_business_rules(self, data: DocumentValidation, results: Dict[str, Any]):
        """Validate business-specific rules"""
        if all(value is not None for value in [data.CommitmentFee, data.SavingsPlanCredit, data.NetPayableFee]):
            calculated_net = data.CommitmentFee - data.SavingsPlanCredit
            if abs(calculated_net - data.NetPayableFee) > 0.01:
                results['warnings'].append("NetPayableFee doesn't match CommitmentFee minus SavingsPlanCredit") 