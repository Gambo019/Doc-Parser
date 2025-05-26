from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DocumentValidation(BaseModel):
    """Document validation model for contract information"""
    CustomerName: str = Field(description="Name of the customer or company (Required but if not applicable, N/A)")
    AccountID: Optional[str] = Field(description="Unique identifier for the customer account (Required but if not applicable, N/A)")
    Quote: Optional[str] = Field(description="Quote number reference")
    CommitmentTerms: Optional[str] = Field(description="Terms of commitment specified in the contract (Required but if not applicable, N/A)")
    BuyingProgram: Optional[str] = Field(description="Type of buying program or plan (Required but if not applicable, N/A)")
    CommitmentFee: Optional[float] = Field(description="Fee amount for the commitment (Required but if not applicable, N/A)")
    SavingsPlanCredit: Optional[float] = Field(description="Credit amount from savings plan (Required but if not applicable, N/A)")
    NetPayableFee: Optional[float] = Field(description="Net fee amount payable (Required but if not applicable, N/A)")
    ContactName: Optional[str] = Field(description="Name of the primary contact person (Required but if not applicable, N/A)")
    TermStartDate: Optional[datetime] = Field(description="Start date of the contract term (Required but if not applicable, N/A)")
    RenewalDate: Optional[datetime] = Field(description="Date when the contract is up for renewal (Required but if not applicable, N/A)")
    BillingTerms: Optional[str] = Field(description="Terms and conditions for billing (Required but if not applicable, N/A)")
    PaymentTerms: Optional[str] = Field(description="Terms and conditions for payment (Required but if not applicable, N/A)")
    PaymentMethod: Optional[str] = Field(description="Method of payment specified (Required but if not applicable, N/A)")
    VATID: Optional[str] = Field(description="VAT identification number")
    PO: Optional[str] = Field(description="Purchase Order number")
    CompanyAddress1: Optional[str] = Field(description="Primary address line of the company (Required but if not applicable, N/A)")
    CompanyAddress2: Optional[str] = Field(description="Secondary address line of the company")
    City: Optional[str] = Field(description="City name from the address")
    State: Optional[str] = Field(description="State or province name")
    Zip: Optional[str] = Field(description="Postal or ZIP code")
    Country: Optional[str] = Field(description="Country name")
    EmailInvoiceTo: Optional[str] = Field(description="Email address for invoice delivery (Required but if not applicable, N/A)")
    CustomerTitle: Optional[str] = Field(description="Title of the customer representative (Required but if not applicable, N/A)")
    DateSigned: Optional[datetime] = Field(description="Date when the document was signed (Required but if not applicable, N/A)")
    CreatedAt: Optional[datetime] = Field(description="Document creation timestamp (Required but if not applicable, N/A)")
    UpdatedAt: Optional[datetime] = Field(description="Last update timestamp (Required but if not applicable, N/A)") 

def get_extraction_prompt_schema() -> str:
    """Generate a string representation of the data model for prompt engineering"""
    
    schema_description = """
{
    "CustomerName": "string - Name of the customer or company (Required)",
    "AccountID": "string - Unique identifier for the customer account (Required)",
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
    "VATID": "string - VAT identification number (Optional)",
    "PO": "string - Purchase Order number (Optional)",
    "CompanyAddress1": "string - Primary address line of the company (Required)",
    "CompanyAddress2": "string - Secondary address line of the company (Optional)",
    "City1": "string - City name from the address (Required)",
    "State1": "string - State or province name (Required)",
    "Zip1": "string - Postal or ZIP code (Required)",
    "Country1": "string - Country name (Required)",
    "City2": "string - City name from the address (Optional)",
    "State2": "string - State or province name (Optional)",
    "Zip2": "string - Postal or ZIP code (Optional)",
    "Country2": "string - Country name (Optional)",
    "EmailInvoiceTo": "string - Email address for invoice delivery (Required)",
    "CustomerTitle": "string - Title of the customer representative (Required)",
    "DateSigned": "string(datetime) - Date when the document was signed in ISO format (YYYY-MM-DD) (Required)",
    "CreatedAt": "string(datetime) - Document creation timestamp in ISO format (YYYY-MM-DDTHH:MM:SS) (Required)",
    "UpdatedAt": "string(datetime) - Last update timestamp in ISO format (YYYY-MM-DDTHH:MM:SS) (Required)"
}
"""
    
    return schema_description 