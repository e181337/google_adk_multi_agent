from src.llm import LlmClient  
from typing import Optional
from dataclasses import dataclass
import json

@dataclass
class IntentTriageResult:
    intent: str
    priority: str
    risk: str

class IntentTriageAgent:

    ALLOWED_INTENTS = {"billing", "technical_support", "account", "compliance", "general",}
    ALLOWED_PRIORITIES = {"low", "medium", "high",}
    ALLOWED_RISKS = {"low", "medium", "high",}
    EXPECTED_KEYS = {"intent", "priority", "risk"}

    def __init__(self, llm_client: LlmClient):
        self.llm_client = llm_client

    def _parse_llm_response(self, raw_response: str) -> dict:
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
    
    def _validate_and_build(self, data: dict) -> IntentTriageResult:
        actual_keys = set(data.keys())
        if actual_keys != self.EXPECTED_KEYS:
            raise ValueError("LLM output key is not correct")
        actual_intent = data["intent"]
        actual_priority = data["priority"]
        actual_risk = data["risk"]
        actual_intent = actual_intent.strip().lower()
        actual_priority = actual_priority.strip().lower()
        actual_risk = actual_risk.strip().lower()
        if actual_intent not in self.ALLOWED_INTENTS:
            raise ValueError("intent is not correct")
        if actual_priority not in self.ALLOWED_PRIORITIES:
            raise ValueError("priority is not correct")
        if actual_risk not in self.ALLOWED_RISKS:
            raise ValueError("risk is not correct")    
        
        result = IntentTriageResult(intent=actual_intent,
                                    priority=actual_priority,
                                    risk = actual_risk)
        return result
    
    def run(self, 
        query_text: str,
        country: Optional[str] = None,
        domain: Optional[str] = None) -> IntentTriageResult:

        if not query_text or not query_text.strip():
            raise ValueError("query_text cannot be empty")
        if not country:
            country = "Unknown"
        if not domain:
            domain = "Unknown"

        system_prompt = """You are a call-center triage classifier.

Classify the incoming customer query into exactly one value for each field below.

Allowed intent values:
- billing
- technical_support
- account
- compliance
- general

Allowed priority values:
- low
- medium
- high

Allowed risk values:
- low
- medium
- high

Return only valid JSON with exactly these keys:
- intent
- priority
- risk

Do not add explanations.
Do not add markdown.
Do not add extra keys.
If the query is ambiguous, choose the closest matching labels."""

        user_prompt = f"""
Classify this customer request.

Query text: {query_text}
Country: {country}
Domain: {domain}"""

        result = self.llm_client.generate(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.0,
            max_output_tokens=100
        )
        result= self._parse_llm_response(result)
        result = self._validate_and_build(result)
        return result
    