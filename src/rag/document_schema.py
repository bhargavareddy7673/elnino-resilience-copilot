"""
Document schema definitions for the Agriculture RAG Knowledge Base.

Defines typed data structures for documents and chunks with complete
metadata tracking for academic rigor and citation provenance.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
import json


@dataclass
class DocumentMetadata:
    """Metadata representing an authentic agricultural source document."""
    document_id: str
    crop: str
    region: str
    language: str
    organization: str
    document_title: str
    publication_date: str
    source_url: str
    file_path: str
    page_count: int = 0
    file_hash: str = ""
    extra_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert document metadata to a JSON-serializable dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentMetadata":
        """Instantiate DocumentMetadata from a dictionary."""
        valid_fields = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


@dataclass
class Chunk:
    """A semantic text chunk with full citation and provenance metadata."""
    chunk_id: str
    document_id: str
    document_title: str
    organization: str
    source_url: str
    publication_date: str
    crop: str
    region: str
    language: str
    page_number: int
    chunk_index: int
    text: str
    token_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to a JSON-serializable dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialize chunk to a JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Chunk":
        """Instantiate Chunk from a dictionary."""
        valid_fields = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

    @classmethod
    def from_json(cls, json_str: str) -> "Chunk":
        """Instantiate Chunk from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
