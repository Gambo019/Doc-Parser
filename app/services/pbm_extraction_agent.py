import openai
from app.models.pbm_contract import get_pbm_extraction_prompt_schema
from app.core.config import settings
from app.core.logger import logger
from typing import Dict, Any
import json

class PBMExtractionAgent:
    """Agent for extracting structured information from PBM contract documents"""
    
    def __init__(self):
        # Set up OpenAI client
        openai.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-4o"
        
    def extract(self, metadata: Dict[str, Any], content: str) -> Dict[str, Any]:
        """Extract structured information from PBM contract document content"""
        try:
            # Get the PBM schema prompt
            schema_prompt = get_pbm_extraction_prompt_schema()
            
            # Combine metadata and content for context
            context = f"Document Metadata:\n{json.dumps(metadata, indent=2)}\n\nDocument Content:\n{content}"
            
            # Create the full prompt with PBM-specific instructions
            full_prompt = f"""
### Schema ###
--------------------------------<Schema-Start>--------------------------------
{schema_prompt}
--------------------------------<Schema-End>--------------------------------

Please extract information from the following PBM (Pharmacy Benefits Management) contract document and return the information in the JSON object following the schema above:

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

6. If a value absolutely does not exist in the document, use null for all fields as they are all optional except contract_type.

7. Return ONLY a valid JSON object, no additional text or explanation

8. For dates, use ISO format (YYYY-MM-DD for dates, YYYY-MM-DDTHH:MM:SS for timestamps) in the format of string.

9. Ensure all field names match exactly as shown above

10. Do not include any fields not listed in the schema
"""
            
            logger.info(f"Sending PBM extraction request to GPT-4o for document with {len(content)} characters")
            
            # Make the API call to OpenAI
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert PBM (Pharmacy Benefits Management) contract analyst. You specialize in extracting structured information from pharmaceutical benefits contracts including MHSA, ASO, and ASA agreements. Extract information accurately and return valid JSON only."
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
            logger.info(f"Received PBM response from GPT-4o: {json_response[:200]}...")
            
            # Parse and return the JSON
            extracted_data = json.loads(json_response)
            return extracted_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from GPT-4o: {str(e)}")
            logger.error(f"Raw response: {json_response}")
            raise ValueError(f"Invalid JSON response from GPT-4o: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error in PBM extraction: {str(e)}")
            raise Exception(f"PBM extraction failed: {str(e)}") 