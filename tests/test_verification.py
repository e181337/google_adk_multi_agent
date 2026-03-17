from src.agents.verification import VerificationAgent, VerificationResult
from src.llm import StaticLlmClient
from src.agents.evidence import EvidenceItem
import json
import pytest

def test_succesfull_result():

    draft_text = "Berlin is the capital of Germany."

    chunk_id = "1"
    doc_id = "Berlin"
    content = "Berlin is the capital and largest city of Germany."

    fixed_response = json.dumps({
        "ok": True,
        "confidence": "high",
        "rationale": "The answer is directly supported by the evidence.",
        "unsupported_claims": []
    })
    model_name = "Gemini"
    llm_client = StaticLlmClient(fixed_response, model_name)

    evidence_items = [EvidenceItem(chunk_id, doc_id, content)]

    verification_client = VerificationAgent(llm_client)

    result = verification_client.run(draft_text, evidence_items)

    assert isinstance(result, VerificationResult)
    assert result.ok == True
    assert result.confidence == "high"
    assert result.rationale == "The answer is directly supported by the evidence."
    assert result.unsupported_claims == []


def test_wrong_json():
    fixed_response = "{ok: value}"
    model_name = "Gemini"
    llm_client = StaticLlmClient(fixed_response, model_name)

    draft_text = "Berlin is the capital of Germany."

    chunk_id = "1"
    doc_id = "Berlin"
    content = "Berlin is the capital and largest city of Germany."
    evidence_items = [EvidenceItem(chunk_id, doc_id, content)]

    verification_client = VerificationAgent(llm_client)

    with pytest.raises(ValueError):
        verification_client.run(draft_text, evidence_items)  

@pytest.mark.parametrize("confidence, expected_result",  
                         [("low", None), 
                          ("medium", None), 
                          ("high", None),
                          (123, TypeError)])
def test_confidence_values(confidence, expected_result):
    fixed_response = json.dumps({
        "ok": True,
        "confidence": confidence,
        "rationale": "Supported.",
        "unsupported_claims": []
    })

    draft_text = "Berlin is the capital of Germany."

    chunk_id = "1"
    doc_id = "Berlin"
    content = "Berlin is the capital and largest city of Germany."

    model_name = "Gemini"
    llm_client = StaticLlmClient(fixed_response, model_name)

    evidence_items = [EvidenceItem(chunk_id, doc_id, content)]

    verification_client = VerificationAgent(llm_client)

    if expected_result is None:
        result = verification_client.run(draft_text, evidence_items)
        assert result.confidence == confidence
    else: 
        with pytest.raises(TypeError):
            verification_client.run(draft_text, evidence_items)



