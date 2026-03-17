from src.agents.evidence import EvidenceItem
from src.agents.grounding import GroundingCitationAgent

def test_empty_draft_text():
    draft_text = ""
    chunk_id = "id1"
    doc_id = "id2"
    content = "This is data"
    evidence_items = EvidenceItem(chunk_id, doc_id, content)
    evidence_items_list = [evidence_items]
    grounding_client = GroundingCitationAgent()
    result = grounding_client.run(draft_text, evidence_items_list)

    assert result.grounded == False
    assert result.citations == [chunk_id]
    
def test_empty_evidence_text():
    draft_text = "This is data"
    evidence_items_list = []
    grounding_client = GroundingCitationAgent()
    result = grounding_client.run(draft_text, evidence_items_list)

    assert result.grounded == False
    assert result.citations == []

def test_grounded_with_valid_evidence():

    draft_text = "This is data"
    evidence_items_list= [EvidenceItem("id1", "doc1", "content1"),EvidenceItem("id2", "doc2", "content2")]
    grounding_client = GroundingCitationAgent()
    result = grounding_client.run(draft_text, evidence_items_list)
    assert result.grounded == True
    assert result.citations == ["id1", "id2"]

def test_citations_empty():
    draft_text = "This is data"
    evidence_items_list= [EvidenceItem("", "doc1", "content1"),EvidenceItem("", "doc2", "content2")]
    grounding_client = GroundingCitationAgent()
    result = grounding_client.run(draft_text, evidence_items_list)
    assert result.grounded == True
    assert result.citations == []