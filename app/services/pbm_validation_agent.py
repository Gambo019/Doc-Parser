from typing import Dict, Any, List, Optional
from pydantic import ValidationError
from datetime import datetime
from app.models.pbm_contract import PBMContractValidation, ContractType
from app.core.logger import logger

class PBMValidationAgent:
    """Agent for validating extracted PBM contract document information"""
    
    def __init__(self):
        self.validation_rules = {
            'date_fields': ['term_start_date', 'renewal_date', 'date_signed'],
            'email_fields': ['email_invoice_to'],
            'required_fields': ['contract_type']
        }
    
    def validate(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted PBM data against rules and return validation results"""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'validated_data': None
        }
        
        try:
            # Check for required contract_type
            if not extracted_data.get('contract_type'):
                validation_results['is_valid'] = False
                validation_results['errors'].append("contract_type is required")
                return validation_results

            # Validate contract_type enum
            contract_type = extracted_data.get('contract_type')
            if contract_type not in [ct.value for ct in ContractType]:
                validation_results['warnings'].append(f"Unknown contract_type: {contract_type}")

            # Basic Pydantic model validation
            validated_data = PBMContractValidation(**extracted_data)
            
            # Custom validation rules
            self._validate_dates(validated_data, validation_results)
            self._validate_email_format(validated_data, validation_results)
            self._validate_pbm_business_rules(validated_data, validation_results)
            
            validation_results['validated_data'] = validated_data.model_dump()
            
        except ValidationError as e:
            validation_results['is_valid'] = False
            validation_results['errors'].extend([str(err) for err in e.errors()])
            logger.error(f"PBM validation error: {str(e)}")
            
        except Exception as e:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Unexpected PBM validation error: {str(e)}")
            logger.error(f"Unexpected PBM validation error: {str(e)}")
            
        return validation_results
    
    def _validate_dates(self, data: PBMContractValidation, results: Dict[str, Any]):
        """Validate date fields"""
        current_date = datetime.now().replace(tzinfo=None)  # Strip timezone info
        
        for field in self.validation_rules['date_fields']:
            date_value = getattr(data, field, None)
            if date_value:
                # Convert to naive datetime for comparison
                if date_value.tzinfo:
                    date_value = date_value.replace(tzinfo=None)
                if date_value > current_date and field != 'renewal_date':
                    results['warnings'].append(f"{field} is in the future")
    
    def _validate_email_format(self, data: PBMContractValidation, results: Dict[str, Any]):
        """Validate email format"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for field in self.validation_rules['email_fields']:
            email = getattr(data, field, None)
            if email and not re.match(email_pattern, email):
                results['warnings'].append(f"Invalid email format in {field}")
    
    def _validate_pbm_business_rules(self, data: PBMContractValidation, results: Dict[str, Any]):
        """Validate PBM-specific business rules"""
        
        # Check if key PBM elements are present
        key_pbm_fields = [
            'awp_pricing_discount_guarantees',
            'retail_brand_30_day_discount',
            'retail_generic_30_day_discount',
            'rebates'
        ]
        
        missing_key_fields = []
        for field in key_pbm_fields:
            if not getattr(data, field, None):
                missing_key_fields.append(field)
        
        if len(missing_key_fields) > 2:
            results['warnings'].append(f"Missing several key PBM contract elements: {', '.join(missing_key_fields)}")
        
        # Validate contract type specific rules
        if data.contract_type == ContractType.MHSA:
            if not data.covered_pharmacy_products_and_services:
                results['warnings'].append("MHSA contracts typically include covered pharmacy products and services")
        
        elif data.contract_type in [ContractType.ASO, ContractType.ASA]:
            if not data.audit_parameters:
                results['warnings'].append("ASO/ASA contracts typically include audit parameters") 