from dataclasses import dataclass
from src.agents.evidence import EvidenceItem
import re 
from src.llm import LlmClient

@dataclass
class DraftingResult:
    draft_text: str
    followups: list[str]

class DraftingAgent:
    def __init__(self, llm_client: LlmClient):
        self.llm_client = llm_client
    
    def _check_type(self, data, data_name: str, data_type: type) -> None:
        if not isinstance(data, data_type):
            raise TypeError(f"{data_name} is not {data_type}")  
    
    def _validate(self, query_text: str, evidence_items: list[EvidenceItem]) -> None:
        self._check_type(query_text, "query_text", str)
        if query_text.strip() == "":
            raise ValueError("query_text is empty")
        self._check_type(evidence_items, "evidence_items", list)
        for value in evidence_items:
            self._check_type(value, "evidence_items values", EvidenceItem)
    
    def _build_prompt(self, query_text: str, evidence_items: list[EvidenceItem]) -> tuple[str, str]:
        content = []
        for value in evidence_items:
            if len(value.content.strip()) > 0:
                content.append(value.content.strip())
        content = "\n".join(content)

        user_prompt = f"""
Question:
{query_text}

Evidence:
{content}
"""
        
        system_prompt = """
You are a call-center compliance assistant.

Your task is to answer the user's question using ONLY the provided evidence.

Rules:
- Use only the information in the evidence.
- If the evidence does not contain the answer, say: "I don't have enough evidence to answer that."
- Do not guess or speculate.
- Do not introduce information not present in the evidence.
- Keep the answer concise and professional.
- Start with a direct answer in 1–2 sentences.
- Then add up to 2–3 bullet points summarizing the key details.
- Do not include citations in the text.
- Maintain a tone suitable for a customer-facing support agent.
"""
        return user_prompt, system_prompt
        
    def run(self, query_text: str, evidence_items: list[EvidenceItem]) -> DraftingResult:

        self._validate(query_text, evidence_items)  

        if not evidence_items:
            return DraftingResult("No evidence found.", 
                                  ["Can you provide more context?", 
                                   "Would you like me to try another search?", 
                                   "Should I answer more generally?"])
        
        
        user_prompt, system_prompt= self._build_prompt(query_text, evidence_items)
        draft_text = self.llm_client.generate(user_prompt=user_prompt, 
                                              system_prompt=system_prompt,
                                              temperature=0.2,
                                              max_output_tokens=300)

        if not isinstance(draft_text, str):
            raise TypeError("llm must return str")
        
        draft_text = draft_text.strip()

        if draft_text == "":
            draft_text = "No answer could be generated from the provided evidence."

        return DraftingResult(draft_text, ["Would you like a shorter answer?",
                                           "Do you want more detail?"])

