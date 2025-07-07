from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List, Any
from enum import Enum

class ContractTypeEnum(str, Enum):
    MHSA = "MHSA"  # Master Health Services Agreement
    ASO = "ASO"    # Administrative Services Only Agreement
    ASA = "ASA"    # Administrative Services Agreement
    OTHER = "OTHER"

class PBMContractValidation(BaseModel):
    """PBM Contract validation model for pharmacy benefits management contract information"""
    
    model_config = ConfigDict(populate_by_name=True)
    
    # Document Type Classification
    ContractType: ContractTypeEnum = Field(description="Type of contract document (MHSA, ASO, ASA, or OTHER)", alias="contract_type")
    
    # Definitions Section
    AverageWholesalePrice: Optional[str] = Field(description="Average Wholesale Price or AWP definition", alias="average_wholesale_price")
    BrandDrug: Optional[str] = Field(description="Brand Drug definition", alias="brand_drug")
    CompoundDrugProduct: Optional[str] = Field(description="Compound Drug Product definition", alias="compound_drug_product")
    CoveredPharmacyProductsAndServices: Optional[str] = Field(description="Covered Pharmacy Products and Services definition", alias="covered_pharmacy_products_and_services")
    GenericDrug: Optional[str] = Field(description="Generic Drug definition", alias="generic_drug")
    MaximumAllowableCost: Optional[str] = Field(description="Maximum Allowable Cost or MAC definition", alias="maximum_allowable_cost")
    DispensingFee: Optional[str] = Field(description="Dispensing Fee definition", alias="dispensing_fee")
    PassThrough: Optional[str] = Field(description="Pass-Through definition", alias="pass_through")
    ProfessionalFee: Optional[str] = Field(description="Professional Fee definition", alias="professional_fee")
    PaidClaim: Optional[str] = Field(description="Paid Claim definition", alias="paid_claim")
    Rebates: Optional[str] = Field(description="Rebate(s) definition", alias="rebates")
    SingleSourceGeneric: Optional[str] = Field(description="Single Source Generic definition", alias="single_source_generic")
    SpecialtyDrugOrSpecialtyProduct: Optional[str] = Field(description="Specialty Drug or Specialty Product definition", alias="specialty_drug_or_specialty_product")
    SpecialtyProductList: Optional[str] = Field(description="Specialty Product List definition", alias="specialty_product_list")
    SpecialtyPharmacy: Optional[str] = Field(description="Specialty Pharmacy definition", alias="specialty_pharmacy")
    MailOrderPharmacy: Optional[str] = Field(description="Mail Order Pharmacy definition", alias="mail_order_pharmacy")
    NetworkPharmacy: Optional[str] = Field(description="Network Pharmacy definition", alias="network_pharmacy")
    UsualAndCustomaryCharge: Optional[str] = Field(description="Usual and Customary Charge or U&C definition", alias="usual_and_customary_charge")
    WholesaleAcquisitionCost: Optional[str] = Field(description="Wholesale Acquisition Cost or WAC definition", alias="wholesale_acquisition_cost")
    IngredientCost: Optional[str] = Field(description="Ingredient Cost definition", alias="ingredient_cost")
    LimitedDistributionDrug: Optional[str] = Field(description="Limited Distribution Drug or LDD definition", alias="limited_distribution_drug")
    LimitedDistributionPharmacy: Optional[str] = Field(description="Limited Distribution Pharmacy or LDD Pharmacy definition", alias="limited_distribution_pharmacy")
    MemberCostShare: Optional[str] = Field(description="Member Cost Share definition", alias="member_cost_share")
    NewToMarket: Optional[str] = Field(description="New to Market definition", alias="new_to_market")
    OverTheCounter: Optional[str] = Field(description="Over-the-Counter or OTC definition", alias="over_the_counter")
    ParticipatingPharmacy: Optional[str] = Field(description="Participating Pharmacy definition", alias="participating_pharmacy")
    SingleSourceGenericDrugs: Optional[str] = Field(description="Single Source Generic Drug(s) or SSG(s) definition", alias="single_source_generic_drugs")
    MedicalBenefitDrugRebate: Optional[str] = Field(description="Medical Benefit Drug Rebate definition", alias="medical_benefit_drug_rebate")
    Network: Optional[str] = Field(description="Network definition", alias="network")
    NetworkProvider: Optional[str] = Field(description="Network Provider definition", alias="network_provider")
    ParticipatingProvider: Optional[str] = Field(description="Participating Provider definition", alias="participating_provider")
    PlanAdministrator: Optional[str] = Field(description="Plan Administrator definition", alias="plan_administrator")
    ProprietaryBusinessInformation: Optional[str] = Field(description="Proprietary Business Information definition", alias="proprietary_business_information")
    TermOrTermOfAgreement: Optional[str] = Field(description="Term or Term of the Agreement definition", alias="term_or_term_of_agreement")
    
    # Financial Guarantees Section
    AwpPricingDiscountGuarantees: Optional[str] = Field(description="AWP Pricing Discount Guarantees details", alias="awp_pricing_discount_guarantees")
    RetailBrand30DayDiscount: Optional[str] = Field(description="30-day Retail Brand and Generic AWP discounts and Dispensing Fee", alias="retail_brand_30_day_discount")
    RetailGeneric30DayDiscount: Optional[str] = Field(description="90-day Retail Brand and Generic AWP discounts and Dispensing Fee", alias="retail_generic_30_day_discount")
    MailDiscounts: Optional[str] = Field(description="Mail discounts for Brand and Generic AWP discounts and Dispensing Fee", alias="mail_discounts")
    RetailSpecialtyDiscounts: Optional[str] = Field(description="Retail Specialty discounts for Brand, Generic, LDD & Exclusive Distribution Drugs", alias="retail_specialty_discounts")
    PricingGuaranteeCalculation: Optional[str] = Field(description="Pricing Guarantee calculation details", alias="pricing_guarantee_calculation")
    PricingGuaranteeExclusionsList: Optional[str] = Field(description="Pricing Guarantee Exclusions list", alias="pricing_guarantee_exclusions_list")
    GuaranteedMinimumRebates: Optional[str] = Field(description="Guaranteed minimum rebates associated with categories", alias="guaranteed_minimum_rebates")
    RebateTermsAndConditions: Optional[str] = Field(description="Rebate terms and conditions", alias="rebate_terms_and_conditions")
    
    # Term and Termination Section
    LengthOfTerm: Optional[str] = Field(description="Length of Term", alias="length_of_term")
    TerminationNotice: Optional[str] = Field(description="Termination Notice details including days, method, caveats, stipulations", alias="termination_notice")
    
    # Audits Section
    AuditParameters: Optional[str] = Field(description="General Audit parameters spelled out in the contract", alias="audit_parameters")
    
    # Fees Section
    FeesDetails: Optional[str] = Field(description="Details about fees, programs offered, and focus areas", alias="fees_details")
    
    # Performance Measures and Performance Guarantees Section
    FeesAtRisk: Optional[str] = Field(description="Fees at risk details", alias="fees_at_risk")
    
    # Common contract fields
    CustomerName: Optional[str] = Field(description="Name of the customer or company", alias="customer_name")
    AccountId: Optional[str] = Field(description="Unique identifier for the customer account", alias="account_id")
    ContactName: Optional[str] = Field(description="Name of the primary contact person", alias="contact_name")
    TermStartDate: Optional[datetime] = Field(description="Start date of the contract term", alias="term_start_date")
    RenewalDate: Optional[datetime] = Field(description="Date when the contract is up for renewal", alias="renewal_date")
    BillingTerms: Optional[str] = Field(description="Terms and conditions for billing", alias="billing_terms")
    PaymentTerms: Optional[str] = Field(description="Terms and conditions for payment", alias="payment_terms")
    PaymentMethod: Optional[str] = Field(description="Method of payment specified", alias="payment_method")
    CompanyAddress1: Optional[str] = Field(description="Primary address line of the company", alias="company_address1")
    CompanyAddress2: Optional[str] = Field(description="Secondary address line of the company", alias="company_address2")
    City: Optional[str] = Field(description="City name from the address", alias="city1")
    State: Optional[str] = Field(description="State or province name", alias="state1")
    ZipCode: Optional[str] = Field(description="Postal or ZIP code", alias="zipcode1")
    Country: Optional[str] = Field(description="Country name", alias="country1")
    EmailInvoiceTo: Optional[str] = Field(description="Email address for invoice delivery", alias="email_invoice_to")
    CustomerTitle: Optional[str] = Field(description="Title of the customer representative", alias="customer_title")
    DateSigned: Optional[datetime] = Field(description="Date when the document was signed", alias="date_signed")
    CreatedAt: Optional[datetime] = Field(description="Document creation timestamp", alias="created_at")
    UpdatedAt: Optional[datetime] = Field(description="Last update timestamp", alias="updated_at")

    @field_validator('TermStartDate', 'RenewalDate', 'DateSigned', 'CreatedAt', 'UpdatedAt', mode='before')
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
    "ContractType": "string - Type of contract document (MHSA, ASO, ASA, or OTHER) (Required)",
    "AverageWholesalePrice": "string - Average Wholesale Price or AWP definition (Required)",
    "BrandDrug": "string - Brand Drug definition (Required)",
    "CompoundDrugProduct": "string - Compound Drug Product definition (Optional)",
    "CoveredPharmacyProductsAndServices": "string - Covered Pharmacy Products and Services definition (Required)",
    "GenericDrug": "string - Generic Drug definition (Required)",
    "MaximumAllowableCost": "string - Maximum Allowable Cost or MAC definition (Required)",
    "DispensingFee": "string - Dispensing Fee definition (Required)",
    "PassThrough": "string - Pass-Through definition (Optional)",
    "ProfessionalFee": "string - Professional Fee definition (Optional)",
    "PaidClaim": "string - Paid Claim definition (Optional)",
    "Rebates": "string - Rebate(s) definition (Required)",
    "SingleSourceGeneric": "string - Single Source Generic definition (Optional)",
    "SpecialtyDrugOrSpecialtyProduct": "string - Specialty Drug or Specialty Product definition (Required)",
    "SpecialtyProductList": "string - Specialty Product List definition (Optional)",
    "SpecialtyPharmacy": "string - Specialty Pharmacy definition (Required)",
    "MailOrderPharmacy": "string - Mail Order Pharmacy definition (Required)",
    "NetworkPharmacy": "string - Network Pharmacy definition (Required)",
    "UsualAndCustomaryCharge": "string - Usual and Customary Charge or U&C definition (Optional)",
    "WholesaleAcquisitionCost": "string - Wholesale Acquisition Cost or WAC definition (Optional)",
    "IngredientCost": "string - Ingredient Cost definition (Optional)",
    "LimitedDistributionDrug": "string - Limited Distribution Drug or LDD definition (Optional)",
    "LimitedDistributionPharmacy": "string - Limited Distribution Pharmacy or LDD Pharmacy definition (Optional)",
    "MemberCostShare": "string - Member Cost Share definition (Optional)",
    "NewToMarket": "string - New to Market definition (Optional)",
    "OverTheCounter": "string - Over-the-Counter or OTC definition (Optional)",
    "ParticipatingPharmacy": "string - Participating Pharmacy definition (Required)",
    "SingleSourceGenericDrugs": "string - Single Source Generic Drug(s) or SSG(s) definition (Optional)",
    "MedicalBenefitDrugRebate": "string - Medical Benefit Drug Rebate definition (Optional)",
    "Network": "string - Network definition (Required)",
    "NetworkProvider": "string - Network Provider definition (Optional)",
    "ParticipatingProvider": "string - Participating Provider definition (Optional)",
    "PlanAdministrator": "string - Plan Administrator definition (Optional)",
    "ProprietaryBusinessInformation": "string - Proprietary Business Information definition (Optional)",
    "TermOrTermOfAgreement": "string - Term or Term of the Agreement definition (Required)",
    "AwpPricingDiscountGuarantees": "string - AWP Pricing Discount Guarantees details (Required)",
    "RetailBrand30DayDiscount": "string - 30-day Retail Brand and Generic AWP discounts and Dispensing Fee (Required)",
    "RetailGeneric30DayDiscount": "string - 90-day Retail Brand and Generic AWP discounts and Dispensing Fee (Required)",
    "MailDiscounts": "string - Mail discounts for Brand and Generic AWP discounts and Dispensing Fee (Required)",
    "RetailSpecialtyDiscounts": "string - Retail Specialty discounts for Brand, Generic, LDD & Exclusive Distribution Drugs (Required)",
    "PricingGuaranteeCalculation": "string - Pricing Guarantee calculation details (Optional)",
    "PricingGuaranteeExclusionsList": "string - Pricing Guarantee Exclusions list (Optional)",
    "GuaranteedMinimumRebates": "string - Guaranteed minimum rebates associated with categories (Required)",
    "RebateTermsAndConditions": "string - Rebate terms and conditions (Required)",
    "LengthOfTerm": "string - Length of Term (Required)",
    "TerminationNotice": "string - Termination Notice details including days, method, caveats, stipulations (Required)",
    "AuditParameters": "string - General Audit parameters spelled out in the contract (Required)",
    "FeesDetails": "string - Details about fees, programs offered, and focus areas (Required)",
    "FeesAtRisk": "string - Fees at risk details (Optional)",
    "CustomerName": "string - Name of the customer or company (Required)",
    "AccountId": "string - Unique identifier for the customer account (Optional)",
    "ContactName": "string - Name of the primary contact person (Required)",
    "TermStartDate": "string(datetime) - Start date of the contract term in ISO format (YYYY-MM-DD) (Required)",
    "RenewalDate": "string(datetime) - Date when the contract is up for renewal in ISO format (YYYY-MM-DD) (Optional)",
    "BillingTerms": "string - Terms and conditions for billing (Optional)",
    "PaymentTerms": "string - Terms and conditions for payment (Optional)",
    "PaymentMethod": "string - Method of payment specified (Optional)",
    "CompanyAddress1": "string - Primary address line of the company (Required)",
    "CompanyAddress2": "string - Secondary address line of the company (Optional)",
    "City": "string - City name from the address (Required)",
    "State": "string - State or province name (Required)",
    "ZipCode": "string - Postal or ZIP code (Required)",
    "Country": "string - Country name (Required)",
    "EmailInvoiceTo": "string - Email address for invoice delivery (Optional)",
    "CustomerTitle": "string - Title of the customer representative (Optional)",
    "DateSigned": "string(datetime) - Date when the document was signed in ISO format (YYYY-MM-DD) (Required)",
    "CreatedAt": "string(datetime) - Document creation timestamp in ISO format (YYYY-MM-DDTHH:MM:SS) (Required)",
    "UpdatedAt": "string(datetime) - Last update timestamp in ISO format (YYYY-MM-DDTHH:MM:SS) (Required)"
}
"""
    
    return schema_description 