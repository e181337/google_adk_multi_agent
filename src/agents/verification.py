from dataclasses import dataclass
from src.llm import LlmClient
from src.agents.evidence import EvidenceItem
import json 

@dataclass
class VerificationResult:
    ok: bool
    confidence: str
    rationale: str
    unsupported_claims: list[str]

class VerificationAgent:
    EXPECTED_KEYS = {"ok", "confidence", "rationale", "unsupported_claims"}
    CONFIDENCE_LEVELS = {"low", "medium", "high"}

    def __init__(self, llm_client:LlmClient):
        self.llm_client = llm_client
    
    def _check_type(self, data, data_name: str, data_type: type) -> None:
        if not isinstance(data, data_type):
            raise TypeError(f"{data_name} is not {data_type}")
    
    def _validate(self, draft_text: str, evidence_items: list[EvidenceItem]) -> None:
        
        self._check_type(draft_text, "draft_text", str)

        self._check_type(evidence_items, "evidence_items", list)

        for value in evidence_items:
            self._check_type(value, "evidence_items", EvidenceItem)           

    def _build_prompt(self, draft_text: str, evidence_items: list[EvidenceItem]) -> tuple[str, str]:

        content = []
        for value in evidence_items:
            if len(value.content.strip()) > 0:
                text = f"""[chunk: {value.chunk_id}]\n{value.content.strip()}"""             
                content.append(text)
        evidence_text = "\n".join(content)

        system_prompt = """
You are a verification agent in a multi-agent RAG system.

Your task is to verify whether the draft answer is fully supported by the provided evidence.

You must evaluate:
- whether the answer is supported by the evidence
- the confidence level of that judgment
- a short rationale
- any unsupported claims

Return only valid JSON with exactly these keys:
- ok
- confidence
- rationale
- unsupported_claims

Rules:
- "ok" must be true only if the answer is supported by the evidence.
- "confidence" must be one of: low, medium, high
- "rationale" must be a short plain-text explanation.
- "unsupported_claims" must be a JSON array of strings.
- If the answer contains claims not grounded in the evidence, list them in "unsupported_claims".
- Do not add markdown.
- Do not add explanations outside JSON.
- Do not add extra keys.
"""
        user_prompt = f"""
Verify the following draft answer against the evidence.

Draft answer:
{draft_text}

Evidence:
{evidence_text}
"""       
        return user_prompt, system_prompt


    def run(self, draft_text: str, evidence_items: list[EvidenceItem]) -> VerificationResult:
        
        self._validate(draft_text, evidence_items)

        if not draft_text or draft_text.strip() == "": 
            return VerificationResult(ok=False, 
                                    confidence="low", 
                                    rationale="Draft text is empty.", 
                                    unsupported_claims=[])
        
        if len(evidence_items) == 0:
            return VerificationResult(ok=False, 
                                    confidence="low", 
                                    rationale="No evidence provided for verification.", 
                                    unsupported_claims=[])
        
        user_prompt, system_prompt = self._build_prompt(draft_text, evidence_items)

        llm_output = self.llm_client.generate(user_prompt=user_prompt, 
                                              system_prompt=system_prompt,
                                              temperature=0.2,
                                              max_output_tokens=300)
        try:
            llm_output_json = json.loads(llm_output)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"json parse error  as {e}")
        
        self._check_type(llm_output_json, "llm_output_json", dict)

        key_set = set(llm_output_json.keys())
        if key_set != self.EXPECTED_KEYS:
            raise ValueError("unexpected key")
        
        self._check_type(llm_output_json["confidence"], "confidence", str)
        if not llm_output_json["confidence"] in self.CONFIDENCE_LEVELS:
            raise ValueError("unexpected confidence key")


        self._check_type(llm_output_json["ok"], "ok", bool)
        
        self._check_type(llm_output_json["rationale"], "rationale", str)

        self._check_type(llm_output_json["unsupported_claims"], "unsupported_claims", list)
        for value in llm_output_json["unsupported_claims"]:
            self._check_type(value, "llm_output_json['unsupported_claims']", str)
            
        
        return VerificationResult(llm_output_json["ok"], 
                                  llm_output_json["confidence"],
                                  llm_output_json["rationale"], 
                                  llm_output_json["unsupported_claims"])