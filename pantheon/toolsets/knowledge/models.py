"""
Knowledge Base Data Model Definitions
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, List
from datetime import datetime


@dataclass
class SourceInfo:
    """Source info (file/folder/URL)."""
    id: str
    collection_id: str
    name: str
    type: str  # "file" | "folder" | "url"
    path: str
    status: str  # "processing" | "active" | "error"
    doc_count: int
    file_types: List[str]
    added_at: float
    error: Optional[str] = None
    progress: Optional[dict] = None  # {current: int, total: int}

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SourceInfo":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class CollectionInfo:
    """Collection info."""
    id: str
    name: str
    description: str
    status: str  # "active" | "error"
    source_ids: List[str]
    total_docs: int
    embedding_model: str
    created_at: float
    updated_at: float

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CollectionInfo":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ChatKnowledgeConfig:
    """Chat knowledge base configuration."""
    chat_id: str
    active_collection_ids: List[str] = field(default_factory=list)
    auto_search: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ChatKnowledgeConfig":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class SearchResult:
    """Search result."""
    id: str
    text: str
    metadata: dict
    score: float
    collection_id: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SearchResult":
        """Create from dictionary."""
        return cls(**data)
