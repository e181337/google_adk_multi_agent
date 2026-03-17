from dataclasses import dataclass
from src.agents.evidence import EvidenceItem

@dataclass
class GroundingResult:
    grounded: bool
    citations: list[str]

class GroundingCitationAgent:
    def _check_type(self, data, data_name: str, data_type: type) -> None:
        if not isinstance(data, data_type):
            raise TypeError(f"{data_name} is not {data_type}")  
    
    def _validate(self, draft_text:str, evidence_items: list[EvidenceItem]) -> None:
        self._check_type(draft_text, "draft_text", str)

        self._check_type(evidence_items, "evidence_items", list)      
        for value in evidence_items:
            self._check_type(value, "evidence_items values", EvidenceItem)

    def run(self, draft_text:str, evidence_items: list[EvidenceItem]) -> GroundingResult:
        self._validate(draft_text, evidence_items)

        grounded = True
        if draft_text.strip() == "":
            grounded = False
        if grounded:
            if len(evidence_items) == 0:
                grounded = False
        
        citations = []
        for value in evidence_items:
            if value.chunk_id:
                citations.append(value.chunk_id)
        
        result = GroundingResult(grounded, citations)
     
        return result