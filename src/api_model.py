from pydantic import BaseModel, Field

class RaqQueryRequest(BaseModel):
    question: str = Field(min_length=1)
    customer_id: str | None =  None
    session_id: str | None =  None
    country: str | None =  None
    topic: str | None =  None
    top_k: int = Field(default=5, ge=1, le=20)
    debug: bool = False


class RagQueryResponse(BaseModel):
    answer: str = Field(min_length=1)
    confidence: str
    rationale: str
    escalation: str | None = None
    followups: list[str]
    evidence: list[dict]
    verifier: dict
    quality: dict
    action: dict
    debug: dict | None = None
