from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, Any

class DocumentValidation(BaseModel):
    """Document validation model for contract information"""
    model_config = ConfigDict(populate_by_name=True)
    
    CustomerName: str = Field(description="Name of the customer or company (Required but if not applicable, N/A)", alias="customer_name")
    AccountId: Optional[str] = Field(description="Unique identifier for the customer account (Required but if not applicable, N/A)", alias="account_id")
    Quote: Optional[str] = Field(description="Quote number reference", alias="quote")
    CommitmentTerms: Optional[str] = Field(description="Terms of commitment specified in the contract (Required but if not applicable, N/A)", alias="commitment_terms")
    BuyingProgram: Optional[str] = Field(description="Type of buying program or plan (Required but if not applicable, N/A)", alias="buying_program")
    CommitmentFee: Optional[float] = Field(description="Fee amount for the commitment (Required but if not applicable, N/A)", alias="commitment_fee")
    SavingsPlanCredit: Optional[float] = Field(description="Credit amount from savings plan (Required but if not applicable, N/A)", alias="savings_plan_credit")
    NetPayableFee: Optional[float] = Field(description="Net fee amount payable (Required but if not applicable, N/A)", alias="net_payable_fee")
    ContactName: Optional[str] = Field(description="Name of the primary contact person (Required but if not applicable, N/A)", alias="contact_name")
    TermStartDate: Optional[datetime] = Field(description="Start date of the contract term (Required but if not applicable, N/A)", alias="term_start_date")
    RenewalDate: Optional[datetime] = Field(description="Date when the contract is up for renewal (Required but if not applicable, N/A)", alias="renewal_date")
    BillingTerms: Optional[str] = Field(description="Terms and conditions for billing (Required but if not applicable, N/A)", alias="billing_terms")
    PaymentTerms: Optional[str] = Field(description="Terms and conditions for payment (Required but if not applicable, N/A)", alias="payment_terms")
    PaymentMethod: Optional[str] = Field(description="Method of payment specified (Required but if not applicable, N/A)", alias="payment_method")
    VatId: Optional[str] = Field(description="VAT identification number", alias="vat_id")
    PurchaseOrderNumber: Optional[str] = Field(description="Purchase Order number", alias="po")
    CompanyAddress1: Optional[str] = Field(description="Primary address line of the company (Required but if not applicable, N/A)", alias="company_address1")
    CompanyAddress2: Optional[str] = Field(description="Secondary address line of the company", alias="company_address2")
    City: Optional[str] = Field(description="City name from the address", alias="city1")
    State: Optional[str] = Field(description="State or province name", alias="state1")
    ZipCode: Optional[str] = Field(description="Postal or ZIP code", alias="zipcode1")
    Country: Optional[str] = Field(description="Country name", alias="country1")
    EmailInvoiceTo: Optional[str] = Field(description="Email address for invoice delivery (Required but if not applicable, N/A)", alias="email_invoice_to")
    CustomerTitle: Optional[str] = Field(description="Title of the customer representative (Required but if not applicable, N/A)", alias="customer_title")
    DateSigned: Optional[datetime] = Field(description="Date when the document was signed (Required but if not applicable, N/A)", alias="date_signed")

    @field_validator('TermStartDate', 'RenewalDate', 'DateSigned', mode='before')
    @classmethod
    def handle_na_dates(cls, v: Any) -> Any:
        """Convert 'N/A' strings to None for date fields"""
        if isinstance(v, str) and v.strip().upper() == 'N/A':
            return None
        return v

def get_extraction_prompt_schema() -> str:
    """Generate a string representation of the data model for prompt engineering"""
    
    schema_description = """
{
    "CustomerName": "string - Name of the customer or company (Required)",
    "AccountId": "string - Unique identifier for the customer account (Required)",
    "Quote": "string - Quote number reference (Optional)",
    "CommitmentTerms": "string - Terms of commitment specified in the contract (Required)",
    "BuyingProgram": "string - Type of buying program or plan (Required)",
    "CommitmentFee": "float - Fee amount for the commitment (Required)",
    "SavingsPlanCredit": "float - Credit amount from savings plan (Required)",
    "NetPayableFee": "float - Net fee amount payable (Required)",
    "ContactName": "string - Name of the primary contact person (Required)",
    "TermStartDate": "string(datetime) - Start date of the contract term in ISO format (YYYY-MM-DD) (Required)",
    "RenewalDate": "string(datetime) - Date when the contract is up for renewal in ISO format (YYYY-MM-DD) (Required)",
    "BillingTerms": "string - Terms and conditions for billing (Required)",
    "PaymentTerms": "string - Terms and conditions for payment (Required)",
    "PaymentMethod": "string - Method of payment specified (Required)",
    "VatId": "string - VAT identification number (Optional)",
    "PurchaseOrderNumber": "string - Purchase Order number (Optional)",
    "CompanyAddress1": "string - Primary address line of the company (Required)",
    "CompanyAddress2": "string - Secondary address line of the company (Optional)",
    "City": "string - City name from the address (Required)",
    "State": "string - State or province name (Required)",
    "ZipCode": "string - Postal or ZIP code (Required)",
    "Country": "string - Country name (Required)",
    "EmailInvoiceTo": "string - Email address for invoice delivery (Required)",
    "CustomerTitle": "string - Title of the customer representative (Required)",
    "DateSigned": "string(datetime) - Date when the document was signed in ISO format (YYYY-MM-DD) (Required)"
}
"""
    
    return schema_description 