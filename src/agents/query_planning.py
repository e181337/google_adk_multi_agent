from dataclasses import dataclass
from src.llm import LlmClient
import json

@dataclass
class QueryPlanningResult:
    rewritten_query: str
    sub_queries: list[str]

class QueryPlanningAgent:
    EXPECTED_KEYS = {"rewritten_query", "sub_queries"}

    def __init__(self, llm_client: LlmClient):
        self.llm_client = llm_client

    def _parse_llm_response(self, raw_response) -> dict:
        if raw_response is None:
            raise ValueError("raw_response is empty")
        if raw_response.strip() == "":
            raise ValueError("raw_response is empty")
        try:
            data = json.loads(raw_response)
            if not isinstance(data, dict):
                raise ValueError("Json is not a dict")
        except json.JSONDecodeError as e :
            raise ValueError(f"Invalid json {e}")
        return data
    
    def _validate_and_build(self, data:dict) -> QueryPlanningResult:
        actual_keys = set(data.keys())
        if actual_keys != self.EXPECTED_KEYS:
            raise ValueError("Unexpected key")
         
        actual_rewritten_query = data["rewritten_query"]
        if not isinstance(actual_rewritten_query, str):
            raise ValueError("actual_rewritten_query is not str")
        if not actual_rewritten_query or actual_rewritten_query.strip() == "":
            raise ValueError("actual_rewritten_query key is empty")
        actual_rewritten_query = actual_rewritten_query.strip()

        actual_sub_queries = data["sub_queries"] 
        if not isinstance(actual_sub_queries, list):
            raise ValueError("actual_sub_queries key is empty") 
        if len(actual_sub_queries) > 3:
            raise ValueError("length of actual_sub_queries is not in correct form") 
        
        for value in actual_sub_queries:
            if not isinstance(value, str) :
                raise ValueError("actual_sub_queries values are not  str") 
            if value.strip() == "" :
                raise ValueError("actual_sub_queries values are empty") 
        
        actual_sub_queries_strip = []
        for values in actual_sub_queries:
            values = values.strip()
            actual_sub_queries_strip.append(values)

        result = QueryPlanningResult(rewritten_query=actual_rewritten_query,
                        sub_queries=actual_sub_queries_strip)
        return result
    
    def run(self, query_text: str,
        intent: str,
        risk: str) -> QueryPlanningResult:

        if not query_text or query_text.strip() == "": 
            raise ValueError("query_text cannot be empty")
        if not intent or intent.strip() == "":
            raise ValueError("intent cannot be empty")
        if not risk or risk.strip() == "":
            raise ValueError("risk cannot be empty")     

        system_prompt = """
You are a query planning agent for a multi-agent RAG system.

Your task is to rewrite the user's query so it is more effective for document retrieval, and to generate a small set of focused sub-queries when useful.

Return only valid JSON with exactly these keys:
- rewritten_query
- sub_queries

Rules:
- rewritten_query must be a concise retrieval-friendly search query.
- sub_queries must be a JSON array of short strings.
- Generate between 0 and 3 sub_queries.
- Do not answer the user question.
- Do not provide explanations.
- Do not add markdown.
- Do not add extra keys.
- Keep all output in English unless the user query clearly requires another language.
- Use the provided intent and risk labels only as context for rewriting and decomposition.
"""  
         
        user_prompt = f"""
Create a retrieval plan for this request.

Query text: {query_text}
Intent: {intent}
Risk: {risk}
"""
        result = self.llm_client.generate(user_prompt=user_prompt,
                                        system_prompt=system_prompt,
                                        temperature=0.0,
                                        max_output_tokens=100)
        result = self._parse_llm_response(result)
        result = self._validate_and_build(result)

        return result
        
        
        