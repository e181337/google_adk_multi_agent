from src.agents.rerank import RerankAgent
from src.agents.evidence import EvidenceItem
import pytest

def test_valid_input():
    query = "python machine learning"
    evidence_item_list = ["Python is a programming language", "Machine learning uses data",
                            "Berlin is the capital of Germany", "Python machine learning tutorial"]
    limit = 2
    result = ["Python machine learning tutorial", "Machine learning uses data"]
    chunk_id = "test"
    doc_id = "test"
    evidence_item = []
    for value in evidence_item_list:
        evidence_item_1 = EvidenceItem(chunk_id=chunk_id, doc_id=doc_id, content=value)
        evidence_item.append(evidence_item_1)

    rerank_client = RerankAgent()
    rerank_result = rerank_client.run(query, evidence_item, limit)

    assert rerank_result.evidence_items[0].content == result[0]
    assert rerank_result.evidence_items[1].content == result[1]
    assert len(rerank_result.evidence_items) == 2

def test_empty_query():
    query = ""
    evidence_items = [EvidenceItem(chunk_id="c1", doc_id="d1", content="Python tutorial")]
    limit = 1
    rerank_client = RerankAgent()
    with pytest.raises(TypeError):
        rerank_client.run(query, evidence_items, limit)

def test_query_normalize_empty():
    query = "!!!"
    evidence_items = [EvidenceItem(chunk_id="c1", doc_id="d1", content="Python tutorial")]
    limit = 1
    rerank_client = RerankAgent()
    with pytest.raises(ValueError):
        rerank_client.run(query, evidence_items, limit)

def test_invalid_evidence_items_type():
    query = "python"
    evidence_items = "not a list"
    limit = 1   
    rerank_client = RerankAgent()
    with pytest.raises(ValueError):
        rerank_client.run(query, evidence_items, limit)

def test_invalid_evidence_item_inside_list():
    query = "python"
    evidence_items = ["wrong type"]
    limit = 1
    rerank_client = RerankAgent()
    with pytest.raises(TypeError):
        rerank_client.run(query, evidence_items, limit)

def test_limit_applied():
    query = "python"
    evidence_items = [
        EvidenceItem(chunk_id="c1", doc_id="d1", content="Python tutorial"),
        EvidenceItem(chunk_id="c2", doc_id="d1", content="Python language basics"),
        EvidenceItem(chunk_id="c3", doc_id="d1", content="Python data science"),
    ]
    limit = 1
    rerank_client = RerankAgent()
    rerank_result = rerank_client.run(query, evidence_items, limit)
    assert len(rerank_result.evidence_items) == limit