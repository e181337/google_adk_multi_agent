from fastapi import APIRouter
from src.api_model import RagQueryResponse, RaqQueryRequest

router = APIRouter()

@router.get("/health", tags=["health"], include_in_schema=False)
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "google-adk-rag-api"}

@router.post("/v1/rag/query", tags=["query"], response_model=RagQueryResponse)
def query(req: RaqQueryRequest) -> RagQueryResponse:
    return RagQueryResponse(
        answer=[],
        confidence=[],
        rationale=[],
        escalation=[],
        followups=[],
        evidence=[],
        verifier={},
        quality={},
        action={},
        debug={}
    )