from dataclasses import dataclass
from typing import Optional

@dataclass
class EvidenceItem:
    chunk_id: str
    doc_id: str
    content: str
    section_path: Optional[str] = None
    score: Optional[float] = None