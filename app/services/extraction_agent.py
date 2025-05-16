from llama_index.llms.openai import OpenAI
from app.models.document import DocumentExtraction, DocumentValidation
from app.core.config import settings
from typing import Dict, Any
import json

class ExtractionAgent:
    """Agent for extracting structured information from documents"""
    
    def __init__(self):
        self.llm = OpenAI(model="gpt-4o")
        
    def extract(self, metadata: Dict[str, Any], content: str) -> Dict[str, Any]:
        """Extract structured information from document content"""
        try:
            try:
                # Convert LLM to structured output
                structured_llm = self.llm.as_structured_llm(DocumentExtraction)
                
                # Combine metadata and content for context
                context = f"Metadata:\n{metadata}\n\nContent:\n{content}"
                
                # Extract structured information
                response = structured_llm.complete(context)
                
                json_response = json.loads(response.text)
                return json_response
            except Exception as e:
                # Convert LLM to structured output
                structured_llm = self.llm.as_structured_llm(DocumentValidation)
                
                # Combine metadata and content for context
                context = f"Metadata:\n{metadata}\n\nContent:\n{content}"
                
                # Extract structured information
                response = structured_llm.complete(context)
                
                json_response = json.loads(response.text)
                return json_response
            
        except Exception as e:
            print(f"Error in extraction: {str(e)}")
            raise 