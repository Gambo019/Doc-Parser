from pydantic import BaseModel, Field
from typing import List, Optional, Union, Any
from enum import Enum

class SourceType(str, Enum):
    PAGE = "page"
    SECTION = "section"
    PARAGRAPH = "paragraph"
    SHEET_CELL = "sheet_cell"
    TEXT_SPAN = "text_span"

class SourceLocation(BaseModel):
    """Base model for source location information"""
    type: SourceType = Field(description="Type of source location")
    reference: str = Field(description="Location reference (e.g., 'page 5', 'Section 2.1', 'Sheet1:A5')")
    text: Optional[str] = Field(default=None, description="Actual text found at this location")

class FieldCitation(BaseModel):
    """Citation information for a single extracted field"""
    value: Any = Field(description="The extracted value")
    sources: List[SourceLocation] = Field(description="List of source locations where this information was found")
    
    @property
    def primary_source(self) -> Optional[SourceLocation]:
        """Get the primary (first) source location"""
        return self.sources[0] if self.sources else None
    
    @property
    def source_summary(self) -> str:
        """Get a summary of all sources"""
        if not self.sources:
            return "No source found"
        elif len(self.sources) == 1:
            return self.sources[0].reference
        else:
            return f"{self.sources[0].reference} (+{len(self.sources)-1} more)"

class DocumentCitations(BaseModel):
    """Container for all field citations in a document"""
    field_citations: dict[str, FieldCitation] = Field(default_factory=dict, description="Citations for each extracted field")
    document_structure: Optional[dict] = Field(default=None, description="Document structure metadata (sections, pages, etc.)")
    
    def add_field_citation(self, field_name: str, value: Any, sources: List[SourceLocation]):
        """Add citation for a field"""
        self.field_citations[field_name] = FieldCitation(value=value, sources=sources)
    
    def get_field_citation(self, field_name: str) -> Optional[FieldCitation]:
        """Get citation for a specific field"""
        return self.field_citations.get(field_name)
    
    def get_all_sources(self) -> List[SourceLocation]:
        """Get all unique source locations used in the document"""
        all_sources = []
        for citation in self.field_citations.values():
            all_sources.extend(citation.sources)
        
        # Remove duplicates based on reference
        unique_sources = []
        seen_refs = set()
        for source in all_sources:
            if source.reference not in seen_refs:
                unique_sources.append(source)
                seen_refs.add(source.reference)
        
        return unique_sources

class StructuredContent(BaseModel):
    """Structured content with source tracking"""
    content: str = Field(description="The actual content text")
    source_location: SourceLocation = Field(description="Where this content was found")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata about this content") 