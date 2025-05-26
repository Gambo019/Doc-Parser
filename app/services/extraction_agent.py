import openai
from app.models.document import get_extraction_prompt_schema
from app.core.config import settings
from app.core.logger import logger
from typing import Dict, Any
import json

class ExtractionAgent:
    """Agent for extracting structured information from documents"""
    
    def __init__(self):
        # Set up OpenAI client
        openai.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-4o"
        
    def extract(self, metadata: Dict[str, Any], content: str) -> Dict[str, Any]:
        """Extract structured information from document content"""
        try:
            # Get the schema prompt
            schema_prompt = get_extraction_prompt_schema()
            
            # Combine metadata and content for context
            context = f"Document Metadata:\n{json.dumps(metadata, indent=2)}\n\nDocument Content:\n{content}"
            
            # Create the full prompt
            full_prompt = f"""
--------------------------------<Instructions-Start>--------------------------------
{schema_prompt}
--------------------------------<Instructions-End>--------------------------------

Please extract information from the following document:

--------------------------------<Document-Start>--------------------------------
{context}
--------------------------------<Document-End>--------------------------------

Return the extracted information as a JSON object following the schema above:
"""
            
            logger.info(f"Content: {full_prompt}")
            
            logger.info(f"Sending extraction request to GPT-4o for document with {len(content)} characters")
            
            # Make the API call to OpenAI
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert document information extraction assistant. Extract structured information from documents and return valid JSON only."
                    },
                    {
                        "role": "user", 
                        "content": full_prompt
                    }
                ],
                temperature=0,  # Low temperature for consistent extraction
                # max_tokens=2000,  # Sufficient for the JSON response
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            # Extract the JSON response
            json_response = response.choices[0].message.content.replace("```json", "").replace("```", "")
            logger.info(f"Received response from GPT-4o: {json_response[:200]}...")
            
            # Parse and return the JSON
            extracted_data = json.loads(json_response)
            return extracted_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response from GPT-4o: {str(e)}")
            logger.error(f"Raw response: {json_response}")
            raise ValueError(f"Invalid JSON response from GPT-4o: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error in extraction: {str(e)}")
            raise Exception(f"Extraction failed: {str(e)}") 