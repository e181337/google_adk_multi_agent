from src.agents.compliance import CompliancePolicyAgent, ComplianceResult, ViolationRule
import pytest

@pytest.mark.parametrize("query_text, draft_text, expected_compliance_ok, expected_violations", 
                         [("My ssn is here", "ok", False, ["ssn"]),
                        ("My social security number is here", "ok", False, ["ssn"]),
                        ("123-45-6789", "ok", False, ["ssn"]),
                        ("ok", "Please send your credit card", False, ["payment_card"]),
                        ("ok", "4111111111111111", False, ["payment_card"]),
                        ("How do I log in?", "Please send your password", False, ["password"]),
                        ("Tell me about Berlin", "Berlin is the capital of Germany.", True, []) ])
def test_ssn(query_text, draft_text, expected_compliance_ok, expected_violations):

    compliance_agent = CompliancePolicyAgent()
    result = compliance_agent.run(query_text, draft_text)
    
    assert result.compliance_ok == expected_compliance_ok
    assert set(result.violations) == set(expected_violations)
    if not expected_compliance_ok:
         assert result.safe_answer == "I cannot process sensitive personal data in chat. Please use secure verified channels."
    else:
        assert result.safe_answer == draft_text