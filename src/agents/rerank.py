from dataclasses import dataclass
from src.agents.evidence import EvidenceItem
import re
@dataclass
class RerankResult:
    evidence_items: list[EvidenceItem]

class RerankAgent:
    def _check_type(self, data, data_name: str, data_type: type) -> None:
        if not isinstance(data, data_type):
            raise ValueError(f"{data_name} is not {data_type}")  
        
    def _validate(self, query_text:str, evidence_items: list[EvidenceItem], limit: int) -> None:
        
        self._check_type(limit, "limit", int)
        if not limit > 0:
            raise TypeError(f"limit less than zero limit: {limit}")
        
        self._check_type(query_text, "query_text", str)
        if not query_text or query_text.strip() == "":
            raise TypeError(f"query_text is empty")
        
        self._check_type(evidence_items, "evidence_items", list)
        for value in evidence_items:
            if not isinstance(value, EvidenceItem):
                raise   TypeError(f"evidence_items values are not EvidenceItem")
            
    def _normalize(self, text: str) -> str:

        text = text.lower().strip()
        text = re.sub("[^\w\s]", "", text)
        return text

        
    def run(self, query_text: str, evidence_items: list[EvidenceItem], limit: int) -> RerankResult:

        self._validate(query_text, evidence_items, limit)
        query_text = self._normalize(query_text)
        if query_text == "":
            raise ValueError("query_text is empty")
        
        query_text_splited = query_text.split()
        token_score = []
        for value in evidence_items:
            value_normalized = self._normalize(value.content)
            value_normalized = value_normalized.split() 
            common_items = list(set(value_normalized) & set(query_text_splited))
            if len(common_items) > 0:
                token_score.append((value, len(common_items)))
        token_score_sorted = sorted(token_score, key=lambda x: x[1], reverse=True)
        token_reranked = token_score_sorted[:limit]
        evidence = []
        for value in token_reranked:
            evidence.append(value[0])
        result = RerankResult(evidence_items=evidence)

        return result


