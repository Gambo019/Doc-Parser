import openai
from app.models.pbm_contract import get_pbm_extraction_prompt_schema
from app.models.citation import DocumentCitations, FieldCitation, SourceLocation, SourceType, StructuredContent
from app.core.config import settings
from app.core.logger import logger
from typing import Dict, Any, List
import json
import re

class PBMExtractionAgentWithCitations:
    """Agent for extracting structured information from PBM contract documents with source attribution"""
    
    def __init__(self):
        # Set up OpenAI client
        openai.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-4o"
        
    def extract(self, metadata: Dict[str, Any], structured_content: List[StructuredContent]) -> Dict[str, Any]:
        """Extract structured information with source citations from PBM contract document content"""
        try:
            # Get the PBM schema prompt
            schema_prompt = get_pbm_extraction_prompt_schema()
            
            # Create content with citation markers
            content_with_citations = self._create_content_with_citations(structured_content)
            
            # Create citation reference map
            citation_map = self._create_citation_map(structured_content)
            
            # Combine metadata and content for context
            context = f"Document Metadata:\n{json.dumps(metadata, indent=2)}\n\nDocument Content with Source Citations:\n{content_with_citations}"
            
            # Create the enhanced prompt with PBM-specific citation instructions
            full_prompt = f"""
### Schema ###
--------------------------------<Schema-Start>--------------------------------
{schema_prompt}
--------------------------------<Schema-End>--------------------------------

Please extract information from the following PBM (Pharmacy Benefits Management) contract document and return the information in a JSON object with SOURCE CITATIONS.

### Document ###
--------------------------------<Document-Start>--------------------------------
{context}
--------------------------------<Document-End>--------------------------------

### Important Instructions ###
1. You MUST identify the contract type first. Look for indicators that suggest:
   - MHSA (Master Health Services Agreement): Comprehensive agreements covering pharmacy services as part of broader healthcare services
   - ASO (Administrative Services Only Agreement): Focus on administrative services for pharmacy benefits
   - ASA (Administrative Services Agreement): Similar to ASO but may have different scope
   - OTHER: If it doesn't clearly fit the above categories

2. Pay special attention to the "Definitions" section which typically contains:
   - Drug pricing terms (AWP, MAC, WAC, U&C)
   - Drug categories (Brand, Generic, Specialty, etc.)
   - Pharmacy types (Network, Mail Order, Specialty, etc.)
   - Service definitions

3. Look for "Financial Guarantees" section containing:
   - AWP discount guarantees
   - Pricing guarantees and exclusions
   - Rebate information

4. Extract "Term and Termination" information including:
   - Contract length
   - Termination notice requirements

5. Find audit-related clauses and fee structures

6. For each extracted field, you MUST provide source citations showing where you found the information.

7. Return a JSON object with this structure:
{{
  "extracted_data": {{
    "FieldName": "extracted_value",
    ...
  }},
  "citations": {{
    "FieldName": {{
      "value": "extracted_value",
      "sources": [
        {{
          "type": "page|section|paragraph|sheet_cell|text_span",
          "reference": "exact citation reference from the document",
          "text": "relevant text snippet from that location"
        }}
      ]
    }},
    ...
  }}
}}

8. If a value absolutely does not exist in the document, use null for all fields regardless of type.

9. For dates and datetimes, use DateTimeOffset format with timezone: YYYY-MM-DDTHH:MM:SS+00:00 (e.g., "2051-01-08T00:00:00+00:00") in string format.

10. When citing sources, use the EXACT citation markers shown in the document (e.g., [page 5], [Section 4.1: Pricing], [paragraph 12]).

11. If information comes from multiple sources (common in PBM contracts), include ALL relevant sources in the sources array.

12. For PBM-specific terms, cite the exact definition location when found.

13. Ensure all field names match exactly as shown in the schema.

14. Do not include any fields not listed in the schema.

### PBM-Specific Citation Examples ###
- Definition citation: {{"type": "section", "reference": "Definitions Section", "text": "Average Wholesale Price (AWP) means the wholesale price..."}}
- Pricing citation: {{"type": "section", "reference": "Section 4.1: Financial Guarantees", "text": "Brand drugs: AWP-15%, Generic: AWP-85%"}}
- Term citation: {{"type": "section", "reference": "Section 8: Term and Termination", "text": "This Agreement shall remain in effect for three (3) years"}}
- Rebate citation: {{"type": "page", "reference": "page 12", "text": "Guaranteed minimum rebate of $2.50 per generic prescription"}}
"""
            
            logger.info(f"Sending PBM extraction request with citations to GPT-4o for document with {len(structured_content)} content sections")
            
            # Make the API call to OpenAI
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert PBM (Pharmacy Benefits Management) contract analyst. You specialize in extracting structured information from pharmaceutical benefits contracts including MHSA, ASO, and ASA agreements with precise source citations. Extract information accurately and return valid JSON only."
                    },
                    {
                        "role": "user", 
                        "content": full_prompt
                    }
                ],
                temperature=0,  # Low temperature for consistent extraction
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            # Extract the JSON response
            json_response = response.choices[0].message.content.replace("```json", "").replace("```", "")
            logger.info(f"Received PBM response from GPT-4o: {json_response[:300]}...")
            
            # Parse the JSON
            response_data = json.loads(json_response)
            
            # Process the response to create proper citation objects
            processed_result = self._process_citation_response(response_data, citation_map, structured_content)
            
            return processed_result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from GPT-4o: {str(e)}")
            logger.error(f"Raw response: {json_response}")
            raise ValueError(f"Invalid JSON response from GPT-4o: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error in PBM extraction with citations: {str(e)}")
            raise Exception(f"PBM extraction with citations failed: {str(e)}")
    
    def _create_content_with_citations(self, structured_content: List[StructuredContent]) -> str:
        """Create content string with embedded citation markers"""
        content_parts = []
        
        for i, content in enumerate(structured_content):
            citation_marker = f"[{content.source_location.reference}]"
            content_parts.append(f"{citation_marker} {content.content}")
        
        return "\n\n".join(content_parts)
    
    def _create_citation_map(self, structured_content: List[StructuredContent]) -> Dict[str, StructuredContent]:
        """Create a map from citation references to structured content"""
        citation_map = {}
        
        for content in structured_content:
            citation_map[content.source_location.reference] = content
        
        return citation_map
    
    def _process_citation_response(self, response_data: Dict[str, Any], citation_map: Dict[str, StructuredContent], structured_content: List[StructuredContent]) -> Dict[str, Any]:
        """Process the AI response to create proper citation objects"""
        extracted_data = response_data.get("extracted_data", {})
        citations_data = response_data.get("citations", {})
        
        # Create DocumentCitations object
        document_citations = DocumentCitations()
        
        # Process each field's citations
        for field_name, citation_info in citations_data.items():
            if isinstance(citation_info, dict) and "sources" in citation_info:
                sources = []
                
                for source_info in citation_info["sources"]:
                    if isinstance(source_info, dict):
                        # Try to match with existing structured content
                        reference = source_info.get("reference", "")
                        source_type = source_info.get("type", "text_span")
                        text = source_info.get("text", "")
                        
                        # Create SourceLocation
                        source_location = SourceLocation(
                            type=SourceType(source_type) if source_type in SourceType.__members__.values() else SourceType.TEXT_SPAN,
                            reference=reference,
                            text=text
                        )
                        sources.append(source_location)
                
                # Add field citation
                if sources:
                    document_citations.add_field_citation(
                        field_name=field_name,
                        value=citation_info.get("value"),
                        sources=sources
                    )
        
        # Add document structure information
        document_structure = {
            "total_sections": len(structured_content),
            "content_types": list(set([content.source_location.type for content in structured_content])),
            "source_summary": {},
            "pbm_specific_sections": self._identify_pbm_sections(structured_content)
        }
        
        # Summarize sources by type
        for content in structured_content:
            source_type = content.source_location.type
            if source_type not in document_structure["source_summary"]:
                document_structure["source_summary"][source_type] = 0
            document_structure["source_summary"][source_type] += 1
        
        document_citations.document_structure = document_structure
        
        return {
            "extracted_data": extracted_data,
            "citations": document_citations.model_dump(),
            "validation_status": self._validate_pbm_citations(document_citations),
            "source_summary": {
                "total_sources": len(document_citations.get_all_sources()),
                "fields_with_citations": len(document_citations.field_citations),
                "citation_coverage": len(document_citations.field_citations) / max(len(extracted_data), 1) * 100
            }
        }
    
    def _identify_pbm_sections(self, structured_content: List[StructuredContent]) -> Dict[str, List[str]]:
        """Identify PBM-specific sections in the document"""
        pbm_sections = {
            "definitions": [],
            "financial_guarantees": [],
            "pricing": [],
            "rebates": [],
            "audits": [],
            "termination": []
        }
        
        for content in structured_content:
            content_lower = content.content.lower()
            reference = content.source_location.reference
            
            # Check for definitions section
            if any(keyword in content_lower for keyword in ["definition", "awp", "average wholesale price", "mac", "maximum allowable cost"]):
                pbm_sections["definitions"].append(reference)
            
            # Check for financial guarantees
            if any(keyword in content_lower for keyword in ["financial guarantee", "pricing guarantee", "discount guarantee"]):
                pbm_sections["financial_guarantees"].append(reference)
            
            # Check for pricing information
            if any(keyword in content_lower for keyword in ["brand drug", "generic drug", "discount", "dispensing fee"]):
                pbm_sections["pricing"].append(reference)
            
            # Check for rebate information
            if any(keyword in content_lower for keyword in ["rebate", "rebates", "guaranteed minimum"]):
                pbm_sections["rebates"].append(reference)
            
            # Check for audit clauses
            if any(keyword in content_lower for keyword in ["audit", "auditing", "audit parameters"]):
                pbm_sections["audits"].append(reference)
            
            # Check for termination clauses
            if any(keyword in content_lower for keyword in ["termination", "term of agreement", "notice period"]):
                pbm_sections["termination"].append(reference)
        
        return pbm_sections
    
    def _validate_pbm_citations(self, document_citations: DocumentCitations) -> Dict[str, Any]:
        """Validate the quality of PBM-specific citations"""
        validation_status = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "citation_quality": "good",
            "pbm_specific_validation": {}
        }
        
        # Check for fields without citations
        fields_without_citations = []
        for field_name, citation in document_citations.field_citations.items():
            if not citation.sources:
                fields_without_citations.append(field_name)
        
        if fields_without_citations:
            validation_status["warnings"].append(f"Fields without citations: {fields_without_citations}")
        
        # PBM-specific validation
        critical_pbm_fields = ["ContractType", "AwpPricingDiscountGuarantees", "GuaranteedMinimumRebates", "LengthOfTerm"]
        missing_critical_citations = []
        
        for field in critical_pbm_fields:
            if field not in document_citations.field_citations or not document_citations.field_citations[field].sources:
                missing_critical_citations.append(field)
        
        if missing_critical_citations:
            validation_status["pbm_specific_validation"]["missing_critical_citations"] = missing_critical_citations
            validation_status["warnings"].append(f"Missing citations for critical PBM fields: {missing_critical_citations}")
        
        # Check citation quality
        total_citations = len(document_citations.field_citations)
        if total_citations == 0:
            validation_status["citation_quality"] = "poor"
            validation_status["errors"].append("No citations found")
        elif len(fields_without_citations) > total_citations * 0.5:
            validation_status["citation_quality"] = "fair"
        
        return validation_status 