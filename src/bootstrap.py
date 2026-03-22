from src.config import (
    get_app_settings,
    get_google_settings,
    get_model_settings,
    get_retrieval_settings,
)
from src.llm import StaticLlmClient, GoogleAdkLlmClient
from src.types import EvidenceItem
from src.agents.intent_triage import IntentTriageAgent
from src.agents.query_planning import QueryPlanningAgent
from src.agents.retrieval import RetrievalAgent
from src.agents.rerank import RerankAgent
from src.agents.grounding import GroundingCitationAgent
from src.agents.drafting import DraftingAgent
from src.agents.verification import VerificationAgent
from src.agents.compliance import CompliancePolicyAgent
from src.agents.risk import RiskAgent
from src.agents.action import ActionWorkflowAgent
from src.agents.escalation import EscalationHandoffAgent
from src.agents.memory import ConversationMemoryAgent
from src.agents.audit import AuditObservabilityAgent
from src.agents.supervisor import OrchestratorSupervisorAgent


def build_knowledge_base() -> list[EvidenceItem]:
    return [
        EvidenceItem(
            chunk_id="c1",
            content="KYC requires identity verification and ongoing monitoring for high-risk customers.",
            score=0.92,
            section_path="policy/kyc.md#section-1",
            doc_id="policy-1",
        ),
        EvidenceItem(
            chunk_id="c2",
            content="Enhanced Due Diligence should be applied when sanctions exposure is detected.",
            score=0.90,
            section_path="policy/sanctions.md#edd",
            doc_id="policy-2",
        ),
        EvidenceItem(
            chunk_id="c3",
            content="For billing disputes, collect invoice details and create a support case within 24 hours.",
            score=0.83,
            section_path="policy/billing.md#disputes",
            doc_id="policy-3",
        ),
    ]

def build_llm_clients(use_real_adk: bool):
    model_settings = get_model_settings()

    if use_real_adk:
        planner_llm = GoogleAdkLlmClient(model_name=model_settings.planner_model)
        answer_llm = GoogleAdkLlmClient(model_name=model_settings.answer_model)
        verifier_llm = GoogleAdkLlmClient(model_name=model_settings.verifier_model)
    else:
        planner_llm = StaticLlmClient(
            fixed_response='{"intent":"compliance","priority":"medium","risk":"medium"}',
            model_name="static-planner",
        )
        answer_llm = StaticLlmClient(
            fixed_response="Use enhanced due diligence when sanctions exposure is detected.",
            model_name="static-answer",
        )
        verifier_llm = StaticLlmClient(
            fixed_response='{"ok": true, "confidence": "high", "rationale": "Supported by evidence.", "unsupported_claims": []}',
            model_name="static-verifier",
        )

    return planner_llm, answer_llm, verifier_llm


def build_orchestrator() -> MultiAgentOrchestrator:
    app_settings = get_app_settings()
    retrieval_settings = get_retrieval_settings()

    planner_llm, answer_llm, verifier_llm = build_llm_clients(
        use_real_adk=False if app_settings.debug else True
    )

    knowledge_base = build_knowledge_base()

    memory_agent = ConversationMemoryAgent()
    audit_agent = AuditObservabilityAgent()
    intent_triage_agent = IntentTriageAgent(planner_llm)
    query_planning_agent = QueryPlanningAgent(planner_llm)
    retrieval_agent = RetrievalAgent(knowledge_base=knowledge_base)
    rerank_agent = RerankAgent()
    grounding_agent = GroundingCitationAgent()
    drafting_agent = DraftingAgent(answer_llm)
    verification_agent = VerificationAgent(verifier_llm)
    compliance_agent = CompliancePolicyAgent()
    risk_agent = RiskAgent()
    action_agent = ActionWorkflowAgent()
    escalation_agent = EscalationHandoffAgent()
    supervisor_agent = OrchestratorSupervisorAgent()

    orchestrator = MultiAgentOrchestrator(
        memory_agent=memory_agent,
        intent_triage_agent=intent_triage_agent,
        query_planning_agent=query_planning_agent,
        retrieval_agent=retrieval_agent,
        rerank_agent=rerank_agent,
        drafting_agent=drafting_agent,
        grounding_agent=grounding_agent,
        verification_agent=verification_agent,
        compliance_agent=compliance_agent,
        risk_agent=risk_agent,
        action_agent=action_agent,
        escalation_agent=escalation_agent,
        audit_agent=audit_agent,
        supervisor_agent=supervisor_agent,
        config=OrchestratorConfig(max_retries=app_settings.debug and 1 or 2),
    )

    return orchestrator

