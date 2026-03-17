from dataclasses import dataclass
from src.agents.evidence import EvidenceItem
import re
@dataclass
class RetrievalResult:
    retrieval_query: str
    evidence_items: list[EvidenceItem]

class RetrievalAgent:
    
    def __init__(self, knowledge_base: list[EvidenceItem]):
        if not knowledge_base:
            raise ValueError("empty knowledge_base data")
        self.knowledge_base = knowledge_base
    
    def _check_type(self, data, data_name: str, data_type: type) -> None:
        if not isinstance(data, data_type):
            raise ValueError(f"{data_name} is not {data_type}")  
    
    def _prepare_inputs(self, rewritten_query: str, sub_queries: list[str]) ->tuple[str, list[str]]:
         
        if not rewritten_query or rewritten_query.strip() == "":
            raise ValueError("rewritten_query cannot be empty")             
        rewritten_query = rewritten_query.lower().strip()
        rewritten_query = re.sub(r"[^\w\s]", "", rewritten_query)        
        if rewritten_query == "":
            raise ValueError("rewritten_query is empty") 

        sub_queries_lower = []
        for value in sub_queries:
            if not value.strip() == "":
                value = value.lower().strip()
                value = re.sub(r"[^\w\s]", "", value)
                if not value.strip() == "":
                    sub_queries_lower.append(value)

        
        return rewritten_query, sub_queries_lower

    def run(self, rewritten_query: str, sub_queries: list[str], limit: int) -> RetrievalResult:
        
        self._check_type(data=rewritten_query, data_name="rewritten_query", data_type=str)
        self._check_type(data=sub_queries, data_name="sub_queries", data_type=list)
        for value in sub_queries:
            self._check_type(data=value, data_name="sub_queries", data_type=str)
        self._check_type(data=limit, data_name="limit", data_type=int)

        if limit <= 0:
            raise ValueError(f"limit is not bigger than 0 {limit}")        

        cleaned_rewritten_query, cleaned_sub_queries = self._prepare_inputs(rewritten_query, sub_queries)
        search_queries = [cleaned_rewritten_query] + cleaned_sub_queries
        search_queries_token = " ".join(search_queries).split() 
        overlap_scores = []
        for item in self.knowledge_base:
            content = item.content
            content = content.lower()
            content = re.sub("[^\w\s]", "", content)
            content_token = content.split()

            overlap = len(list(set(content_token) & set(search_queries_token)))
            if overlap > 0:
                overlap_scores.append((item, overlap))
        
        sorted_content_overlap = sorted(overlap_scores, key= lambda x: x[1], reverse=True)   
        evidence_items = []
        for value in sorted_content_overlap[:limit]:
            evidence_items.append(value[0])
    
        result = RetrievalResult(retrieval_query=rewritten_query,
                                evidence_items=evidence_items)
        
        return result

    

