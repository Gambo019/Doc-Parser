from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Any
from enum import Enum

class ContractType(str, Enum):
    MHSA = "MHSA"  # Master Health Services Agreement
    ASO = "ASO"    # Administrative Services Only Agreement
    ASA = "ASA"    # Administrative Services Agreement
    OTHER = "OTHER"

class PBMContractValidation(BaseModel):
    """PBM Contract validation model for pharmacy benefits management contract information"""
    
    # Document Type Classification
    contract_type: ContractType = Field(description="Type of contract document (MHSA, ASO, ASA, or OTHER)")
    
    # Definitions Section
    average_wholesale_price: Optional[str] = Field(description="Average Wholesale Price or AWP definition")
    brand_drug: Optional[str] = Field(description="Brand Drug definition")
    compound_drug_product: Optional[str] = Field(description="Compound Drug Product definition")
    covered_pharmacy_products_and_services: Optional[str] = Field(description="Covered Pharmacy Products and Services definition")
    generic_drug: Optional[str] = Field(description="Generic Drug definition")
    maximum_allowable_cost: Optional[str] = Field(description="Maximum Allowable Cost or MAC definition")
    dispensing_fee: Optional[str] = Field(description="Dispensing Fee definition")
    pass_through: Optional[str] = Field(description="Pass-Through definition")
    professional_fee: Optional[str] = Field(description="Professional Fee definition")
    paid_claim: Optional[str] = Field(description="Paid Claim definition")
    rebates: Optional[str] = Field(description="Rebate(s) definition")
    single_source_generic: Optional[str] = Field(description="Single Source Generic definition")
    specialty_drug_or_specialty_product: Optional[str] = Field(description="Specialty Drug or Specialty Product definition")
    specialty_product_list: Optional[str] = Field(description="Specialty Product List definition")
    specialty_pharmacy: Optional[str] = Field(description="Specialty Pharmacy definition")
    mail_order_pharmacy: Optional[str] = Field(description="Mail Order Pharmacy definition")
    network_pharmacy: Optional[str] = Field(description="Network Pharmacy definition")
    usual_and_customary_charge: Optional[str] = Field(description="Usual and Customary Charge or U&C definition")
    wholesale_acquisition_cost: Optional[str] = Field(description="Wholesale Acquisition Cost or WAC definition")
    ingredient_cost: Optional[str] = Field(description="Ingredient Cost definition")
    limited_distribution_drug: Optional[str] = Field(description="Limited Distribution Drug or LDD definition")
    limited_distribution_pharmacy: Optional[str] = Field(description="Limited Distribution Pharmacy or LDD Pharmacy definition")
    member_cost_share: Optional[str] = Field(description="Member Cost Share definition")
    new_to_market: Optional[str] = Field(description="New to Market definition")
    over_the_counter: Optional[str] = Field(description="Over-the-Counter or OTC definition")
    participating_pharmacy: Optional[str] = Field(description="Participating Pharmacy definition")
    single_source_generic_drugs: Optional[str] = Field(description="Single Source Generic Drug(s) or SSG(s) definition")
    medical_benefit_drug_rebate: Optional[str] = Field(description="Medical Benefit Drug Rebate definition")
    network: Optional[str] = Field(description="Network definition")
    network_provider: Optional[str] = Field(description="Network Provider definition")
    participating_provider: Optional[str] = Field(description="Participating Provider definition")
    plan_administrator: Optional[str] = Field(description="Plan Administrator definition")
    proprietary_business_information: Optional[str] = Field(description="Proprietary Business Information definition")
    term_or_term_of_agreement: Optional[str] = Field(description="Term or Term of the Agreement definition")
    
    # Financial Guarantees Section
    awp_pricing_discount_guarantees: Optional[str] = Field(description="AWP Pricing Discount Guarantees details")
    retail_brand_30_day_discount: Optional[str] = Field(description="30-day Retail Brand and Generic AWP discounts and Dispensing Fee")
    retail_generic_30_day_discount: Optional[str] = Field(description="90-day Retail Brand and Generic AWP discounts and Dispensing Fee")
    mail_discounts: Optional[str] = Field(description="Mail discounts for Brand and Generic AWP discounts and Dispensing Fee")
    retail_specialty_discounts: Optional[str] = Field(description="Retail Specialty discounts for Brand, Generic, LDD & Exclusive Distribution Drugs")
    pricing_guarantee_calculation: Optional[str] = Field(description="Pricing Guarantee calculation details")
    pricing_guarantee_exclusions_list: Optional[str] = Field(description="Pricing Guarantee Exclusions list")
    guaranteed_minimum_rebates: Optional[str] = Field(description="Guaranteed minimum rebates associated with categories")
    rebate_terms_and_conditions: Optional[str] = Field(description="Rebate terms and conditions")
    
    # Term and Termination Section
    length_of_term: Optional[str] = Field(description="Length of Term")
    termination_notice: Optional[str] = Field(description="Termination Notice details including days, method, caveats, stipulations")
    
    # Audits Section
    audit_parameters: Optional[str] = Field(description="General Audit parameters spelled out in the contract")
    
    # Fees Section
    fees_details: Optional[str] = Field(description="Details about fees, programs offered, and focus areas")
    
    # Performance Measures and Performance Guarantees Section
    fees_at_risk: Optional[str] = Field(description="Fees at risk details")
    
    # Common contract fields
    customer_name: Optional[str] = Field(description="Name of the customer or company")
    account_id: Optional[str] = Field(description="Unique identifier for the customer account")
    contact_name: Optional[str] = Field(description="Name of the primary contact person")
    term_start_date: Optional[datetime] = Field(description="Start date of the contract term")
    renewal_date: Optional[datetime] = Field(description="Date when the contract is up for renewal")
    billing_terms: Optional[str] = Field(description="Terms and conditions for billing")
    payment_terms: Optional[str] = Field(description="Terms and conditions for payment")
    payment_method: Optional[str] = Field(description="Method of payment specified")
    company_address1: Optional[str] = Field(description="Primary address line of the company")
    company_address2: Optional[str] = Field(description="Secondary address line of the company")
    city1: Optional[str] = Field(description="City name from the address")
    state1: Optional[str] = Field(description="State or province name")
    zipcode1: Optional[str] = Field(description="Postal or ZIP code")
    country1: Optional[str] = Field(description="Country name")
    email_invoice_to: Optional[str] = Field(description="Email address for invoice delivery")
    customer_title: Optional[str] = Field(description="Title of the customer representative")
    date_signed: Optional[datetime] = Field(description="Date when the document was signed")
    created_at: Optional[datetime] = Field(description="Document creation timestamp")
    updated_at: Optional[datetime] = Field(description="Last update timestamp")

    @field_validator('term_start_date', 'renewal_date', 'date_signed', 'created_at', 'updated_at', mode='before')
    @classmethod
    def handle_na_dates(cls, v: Any) -> Any:
        """Convert 'N/A' strings to None for date fields"""
        if isinstance(v, str) and v.strip().upper() == 'N/A':
            return None
        return v

def get_pbm_extraction_prompt_schema() -> str:
    """Generate a string representation of the PBM contract data model for prompt engineering"""
    
    schema_description = """
{
    "contract_type": "string - Type of contract document (MHSA, ASO, ASA, or OTHER) (Required)",
    "average_wholesale_price": "string - Average Wholesale Price or AWP definition (Required)",
    "brand_drug": "string - Brand Drug definition (Required)",
    "compound_drug_product": "string - Compound Drug Product definition (Optional)",
    "covered_pharmacy_products_and_services": "string - Covered Pharmacy Products and Services definition (Required)",
    "generic_drug": "string - Generic Drug definition (Required)",
    "maximum_allowable_cost": "string - Maximum Allowable Cost or MAC definition (Required)",
    "dispensing_fee": "string - Dispensing Fee definition (Required)",
    "pass_through": "string - Pass-Through definition (Optional)",
    "professional_fee": "string - Professional Fee definition (Optional)",
    "paid_claim": "string - Paid Claim definition (Optional)",
    "rebates": "string - Rebate(s) definition (Required)",
    "single_source_generic": "string - Single Source Generic definition (Optional)",
    "specialty_drug_or_specialty_product": "string - Specialty Drug or Specialty Product definition (Required)",
    "specialty_product_list": "string - Specialty Product List definition (Optional)",
    "specialty_pharmacy": "string - Specialty Pharmacy definition (Required)",
    "mail_order_pharmacy": "string - Mail Order Pharmacy definition (Required)",
    "network_pharmacy": "string - Network Pharmacy definition (Required)",
    "usual_and_customary_charge": "string - Usual and Customary Charge or U&C definition (Optional)",
    "wholesale_acquisition_cost": "string - Wholesale Acquisition Cost or WAC definition (Optional)",
    "ingredient_cost": "string - Ingredient Cost definition (Optional)",
    "limited_distribution_drug": "string - Limited Distribution Drug or LDD definition (Optional)",
    "limited_distribution_pharmacy": "string - Limited Distribution Pharmacy or LDD Pharmacy definition (Optional)",
    "member_cost_share": "string - Member Cost Share definition (Optional)",
    "new_to_market": "string - New to Market definition (Optional)",
    "over_the_counter": "string - Over-the-Counter or OTC definition (Optional)",
    "participating_pharmacy": "string - Participating Pharmacy definition (Required)",
    "single_source_generic_drugs": "string - Single Source Generic Drug(s) or SSG(s) definition (Optional)",
    "medical_benefit_drug_rebate": "string - Medical Benefit Drug Rebate definition (Optional)",
    "network": "string - Network definition (Required)",
    "network_provider": "string - Network Provider definition (Optional)",
    "participating_provider": "string - Participating Provider definition (Optional)",
    "plan_administrator": "string - Plan Administrator definition (Optional)",
    "proprietary_business_information": "string - Proprietary Business Information definition (Optional)",
    "term_or_term_of_agreement": "string - Term or Term of the Agreement definition (Required)",
    "awp_pricing_discount_guarantees": "string - AWP Pricing Discount Guarantees details (Required)",
    "retail_brand_30_day_discount": "string - 30-day Retail Brand and Generic AWP discounts and Dispensing Fee (Required)",
    "retail_generic_30_day_discount": "string - 90-day Retail Brand and Generic AWP discounts and Dispensing Fee (Required)",
    "mail_discounts": "string - Mail discounts for Brand and Generic AWP discounts and Dispensing Fee (Required)",
    "retail_specialty_discounts": "string - Retail Specialty discounts for Brand, Generic, LDD & Exclusive Distribution Drugs (Required)",
    "pricing_guarantee_calculation": "string - Pricing Guarantee calculation details (Optional)",
    "pricing_guarantee_exclusions_list": "string - Pricing Guarantee Exclusions list (Optional)",
    "guaranteed_minimum_rebates": "string - Guaranteed minimum rebates associated with categories (Required)",
    "rebate_terms_and_conditions": "string - Rebate terms and conditions (Required)",
    "length_of_term": "string - Length of Term (Required)",
    "termination_notice": "string - Termination Notice details including days, method, caveats, stipulations (Required)",
    "audit_parameters": "string - General Audit parameters spelled out in the contract (Required)",
    "fees_details": "string - Details about fees, programs offered, and focus areas (Required)",
    "fees_at_risk": "string - Fees at risk details (Optional)",
    "customer_name": "string - Name of the customer or company (Required)",
    "account_id": "string - Unique identifier for the customer account (Optional)",
    "contact_name": "string - Name of the primary contact person (Required)",
    "term_start_date": "string(datetime) - Start date of the contract term in ISO format (YYYY-MM-DD) (Required)",
    "renewal_date": "string(datetime) - Date when the contract is up for renewal in ISO format (YYYY-MM-DD) (Optional)",
    "billing_terms": "string - Terms and conditions for billing (Optional)",
    "payment_terms": "string - Terms and conditions for payment (Optional)",
    "payment_method": "string - Method of payment specified (Optional)",
    "company_address1": "string - Primary address line of the company (Required)",
    "company_address2": "string - Secondary address line of the company (Optional)",
    "city1": "string - City name from the address (Required)",
    "state1": "string - State or province name (Required)",
    "zipcode1": "string - Postal or ZIP code (Required)",
    "country1": "string - Country name (Required)",
    "city2": "string - City name from the address (Optional)",
    "state2": "string - State or province name (Optional)",
    "zipcode2": "string - Postal or ZIP code (Optional)",
    "country2": "string - Country name (Optional)",
    "email_invoice_to": "string - Email address for invoice delivery (Optional)",
    "customer_title": "string - Title of the customer representative (Optional)",
    "date_signed": "string(datetime) - Date when the document was signed in ISO format (YYYY-MM-DD) (Required)",
    "created_at": "string(datetime) - Document creation timestamp in ISO format (YYYY-MM-DDTHH:MM:SS) (Required)",
    "updated_at": "string(datetime) - Last update timestamp in ISO format (YYYY-MM-DDTHH:MM:SS) (Required)"
}
"""
    
    return schema_description 