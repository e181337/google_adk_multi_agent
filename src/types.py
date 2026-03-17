from dataclasses import dataclass, field
from typing import Optional

@dataclass
class EvidenceItem:
    chunk_id: str
    content: str
    score: float
    section_path: Optional[str] = None
    doc_id: Optional[str] = None

@dataclass
class QueryRequest:
    query_text: str
    customer_id: Optional[str] = None
    session_id: Optional[str] = None
    country: Optional[str] = None
    domain: Optional[str] = None
    limit: int = 5
    include_debug: bool =False

@dataclass
class QueryResponse:
    answer: str
    confidence: str
    rationale: str
    escalation: str | None
    followups: list[str]
    evidence: list[EvidenceItem] 
    verifier: dict
    quality: dict
    action: dict
    debug: dict | None
