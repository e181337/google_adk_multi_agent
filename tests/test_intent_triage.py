from typing import Optional
from src.agents.intent_triage import IntentTriageAgent, IntentTriageResult
import pytest

class FakeLlmClient:
    def __init__(self, response:str):
        self.response = response
    
    def generate(self, user_prompt:str, 
                 system_prompt: Optional[str] = None,
                 temperature: Optional[float] = None,
                 max_output_tokens: Optional[int] = None,) -> str:
        return self.response
    

def test_intent_triage_result():

    response = '{"intent": "billing","priority": "high", "risk": "low"}'

    fake_client = FakeLlmClient(response)
    agent = IntentTriageAgent(fake_client)
    result = agent.run(query_text="problem with invoice")

    assert type(result) == IntentTriageResult
    assert result.intent == "billing"
    assert result.priority == "high"
    assert result.risk == "low"

def test_run_fails_when_query_text_empty():
    response = '{"intent":"billing","priority":"high","risk":"low"}'
    fake_client = FakeLlmClient(response)
    agent = IntentTriageAgent(fake_client)
    with pytest.raises(ValueError):
        agent.run(query_text="")

def test_run_fails_when_llm_returns_empty_strin():
    response = ""
    fake_client = FakeLlmClient(response)
    agent = IntentTriageAgent(fake_client)
    with pytest.raises(ValueError):
        agent.run("problem with invoice")

def test_run_fails_when_not_json():
    response = '["billing","high","low"]'
    fake_client = FakeLlmClient(response)
    agent = IntentTriageAgent(fake_client)
    with pytest.raises(ValueError):
        agent.run("problem with invoice")

def test_invalid_JSON_string():
    response = "{bad json}"
    fake_client = FakeLlmClient(response)
    agent = IntentTriageAgent(fake_client)
    with pytest.raises(ValueError):
        agent.run("problem with invoice")

def test_missing_key():
    response = '{"intent":"billing","priority":"high"}'
    fake_client = FakeLlmClient(response)
    agent = IntentTriageAgent(fake_client)
    with pytest.raises(ValueError):
        agent.run("problem with invoice")

