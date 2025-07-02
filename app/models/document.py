from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DocumentValidation(BaseModel):
    """Document validation model for contract information"""
    customer_name: str = Field(description="Name of the customer or company (Required but if not applicable, N/A)")
    account_id: Optional[str] = Field(description="Unique identifier for the customer account (Required but if not applicable, N/A)")
    quote: Optional[str] = Field(description="Quote number reference")
    commitment_terms: Optional[str] = Field(description="Terms of commitment specified in the contract (Required but if not applicable, N/A)")
    buying_program: Optional[str] = Field(description="Type of buying program or plan (Required but if not applicable, N/A)")
    commitment_fee: Optional[float] = Field(description="Fee amount for the commitment (Required but if not applicable, N/A)")
    savings_plan_credit: Optional[float] = Field(description="Credit amount from savings plan (Required but if not applicable, N/A)")
    net_payable_fee: Optional[float] = Field(description="Net fee amount payable (Required but if not applicable, N/A)")
    contact_name: Optional[str] = Field(description="Name of the primary contact person (Required but if not applicable, N/A)")
    term_start_date: Optional[datetime] = Field(description="Start date of the contract term (Required but if not applicable, N/A)")
    renewal_date: Optional[datetime] = Field(description="Date when the contract is up for renewal (Required but if not applicable, N/A)")
    billing_terms: Optional[str] = Field(description="Terms and conditions for billing (Required but if not applicable, N/A)")
    payment_terms: Optional[str] = Field(description="Terms and conditions for payment (Required but if not applicable, N/A)")
    payment_method: Optional[str] = Field(description="Method of payment specified (Required but if not applicable, N/A)")
    vat_id: Optional[str] = Field(description="VAT identification number")
    po: Optional[str] = Field(description="Purchase Order number")
    company_address1: Optional[str] = Field(description="Primary address line of the company (Required but if not applicable, N/A)")
    company_address2: Optional[str] = Field(description="Secondary address line of the company")
    city1: Optional[str] = Field(description="City name from the address")
    state1: Optional[str] = Field(description="State or province name")
    zipcode1: Optional[str] = Field(description="Postal or ZIP code")
    country1: Optional[str] = Field(description="Country name")
    email_invoice_to: Optional[str] = Field(description="Email address for invoice delivery (Required but if not applicable, N/A)")
    customer_title: Optional[str] = Field(description="Title of the customer representative (Required but if not applicable, N/A)")
    date_signed: Optional[datetime] = Field(description="Date when the document was signed (Required but if not applicable, N/A)")
    created_at: Optional[datetime] = Field(description="Document creation timestamp (Required but if not applicable, N/A)")
    updated_at: Optional[datetime] = Field(description="Last update timestamp (Required but if not applicable, N/A)") 

def get_extraction_prompt_schema() -> str:
    """Generate a string representation of the data model for prompt engineering"""
    
    schema_description = """
{
    "customer_name": "string - Name of the customer or company (Required)",
    "account_id": "string - Unique identifier for the customer account (Required)",
    "quote": "string - Quote number reference (Optional)",
    "commitment_terms": "string - Terms of commitment specified in the contract (Required)",
    "buying_program": "string - Type of buying program or plan (Required)",
    "commitment_fee": "float - Fee amount for the commitment (Required)",
    "savings_plan_credit": "float - Credit amount from savings plan (Required)",
    "net_payable_fee": "float - Net fee amount payable (Required)",
    "contact_name": "string - Name of the primary contact person (Required)",
    "term_start_date": "string(datetime) - Start date of the contract term in ISO format (YYYY-MM-DD) (Required)",
    "renewal_date": "string(datetime) - Date when the contract is up for renewal in ISO format (YYYY-MM-DD) (Required)",
    "billing_terms": "string - Terms and conditions for billing (Required)",
    "payment_terms": "string - Terms and conditions for payment (Required)",
    "payment_method": "string - Method of payment specified (Required)",
    "vat_id": "string - VAT identification number (Optional)",
    "po": "string - Purchase Order number (Optional)",
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
    "email_invoice_to": "string - Email address for invoice delivery (Required)",
    "customer_title": "string - Title of the customer representative (Required)",
    "date_signed": "string(datetime) - Date when the document was signed in ISO format (YYYY-MM-DD) (Required)",
    "created_at": "string(datetime) - Document creation timestamp in ISO format (YYYY-MM-DDTHH:MM:SS) (Required)",
    "updated_at": "string(datetime) - Last update timestamp in ISO format (YYYY-MM-DDTHH:MM:SS) (Required)"
}
"""
    
    return schema_description 