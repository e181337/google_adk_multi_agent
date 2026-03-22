from dataclasses import dataclass
import uuid

from src.types import QueryRequest, QueryResponse
from src.agents.intent_triage import IntentTriageAgent
from src.agents.query_planning import QueryPlanningAgent
from src.agents.retrieval import RetrievalAgent
from src.agents.rerank import RerankAgent
from src.agents.drafting import DraftingAgent
from src.agents.grounding import GroundingCitationAgent
from src.agents.verification import VerificationAgent
from src.agents.compliance import CompliancePolicyAgent
from src.agents.risk import RiskAgent
from src.agents.action import ActionWorkflowAgent
from src.agents.escalation import EscalationHandoffAgent
from src.agents.memory import ConversationMemoryAgent
from src.agents.audit import AuditObservabilityAgent
from src.agents.supervisor import OrchestratorSupervisorAgent

@dataclass
class OrchestratorConfig:
    max_retries: int = 2

class MultiAgentOrchestrator:

    def __init__(self,
            memory_agent: ConversationMemoryAgent,
            triage_agent: IntentTriageAgent,
            planning_agent: QueryPlanningAgent,
            retrieval_agent: RetrievalAgent,
            rerank_agent: RerankAgent,
            drafting_agent: DraftingAgent,
            grounding_agent: GroundingCitationAgent,
            verification_agent: VerificationAgent,
            compliance_agent: CompliancePolicyAgent,
            risk_agent: RiskAgent,
            action_agent: ActionWorkflowAgent,
            escalation_agent: EscalationHandoffAgent,
            audit_agent: AuditObservabilityAgent,
            supervisor_agent: OrchestratorSupervisorAgent,
            config: OrchestratorConfig | None = None,) -> None:
        
        self.memory_agent = memory_agent
        self.triage_agent = triage_agent
        self.planning_agent = planning_agent
        self.retrieval_agent = retrieval_agent
        self.rerank_agent = rerank_agent
        self.drafting_agent = drafting_agent
        self.grounding_agent = grounding_agent
        self.verification_agent = verification_agent
        self.compliance_agent = compliance_agent
        self.risk_agent = risk_agent
        self.action_agent = action_agent
        self.escalation_agent = escalation_agent
        self.audit_agent = audit_agent
        self.supervisor_agent = supervisor_agent
        self.config = config

    def _audit(self, trace_id: str, stage: str, payload: dict) -> None:
        self.audit_agent.run(trace_id=trace_id, stage=stage, payload=payload)

    def run(self, request: QueryRequest) -> QueryResponse:
        trace_id = request.session_id or uuid.uuid4()

        self._audit(trace_id, "request_received",
            {
                "query_text": request.query_text,
                "customer_id": request.customer_id,
                "country": request.country,
                "domain": request.domain,
            },
        )

        memory_result = self.memory_agent.run(
            session_id=trace_id,
            query_text=request.query_text,
        )

        triage_result = self.triage_agent.run(
            query_text=request.query_text,
            country=request.country,
            domain=request.domain,
        )

        planning_result = self.planning_agent.run(
            query_text=request.query_text,
            intent=triage_result.intent,
            risk=triage_result.risk,
        )

        evidence_items = []
        draft_result = None
        grounding_result = None
        verification_result = None
        compliance_result = None

        for attempt in range(1, self.config.max_retries + 1):
            retrieval_result = self.retrieval_agent.run(
                rewritten_query=planning_result.rewritten_query,
                sub_queries=planning_result.sub_queries,
                limit=request.limit,
            )

            rerank_result = self.rerank_agent.run(
                query_text=request.query_text,
                evidence_items=retrieval_result.evidence_items,
                limit=request.limit,
            )

            evidence_items = rerank_result.evidence_items

            draft_result = self.drafting_agent.run(
                query_text=request.query_text,
                evidence_items=evidence_items,
            )

            grounding_result = self.grounding_agent.run(
                draft_text=draft_result.draft_text,
                evidence_items=evidence_items,
            )

            verification_result = self.verification_agent.run(
                draft_text=draft_result.draft_text,
                evidence_items=evidence_items,
            )

            compliance_result = self.compliance_agent.run(
                query_text=request.query_text,
                draft_text=draft_result.draft_text,
            )

            supervisor_result = self.supervisor_agent.run(
                attempt=attempt,
                verification_ok=verification_result.ok,
                compliance_ok=compliance_result.compliance_ok,
                max_retries=self.config.max_retries,
            )

            self._audit(
                trace_id,
                "attempt_completed",
                {
                    "attempt": attempt,
                    "verification_ok": verification_result.ok,
                    "compliance_ok": compliance_result.compliance_ok,
                    "retry": supervisor_result.retry,
                },
            )

            if not supervisor_result.retry:
                break

        if draft_result is None or verification_result is None or compliance_result is None or grounding_result is None:
            raise RuntimeError("Orchestrator failed to produce required intermediate results")

        risk_result = self.risk_agent.run(
            query_text=request.query_text,
            verification_ok=verification_result.ok,
            compliance_ok=compliance_result.compliance_ok,
        )

        action_result = self.action_agent.run(
            intent=triage_result.intent,
            priority=triage_result.priority,
            compliance_ok=compliance_result.compliance_ok,
        )

        escalation_result = self.escalation_agent.run(
            risk=risk_result.risk,
            verification_ok=verification_result.ok,
            compliance_ok=compliance_result.compliance_ok,
            query_text=request.query_text,
        )

        final_answer = compliance_result.safe_answer
        if compliance_result.compliance_ok:
            final_answer = draft_result.draft_text

        quality = {
            "grounded": grounding_result.grounded,
            "citation_count": len(grounding_result.citations),
            "risk": risk_result.risk,
        }

        debug = None
        if request.include_debug:
            debug = {
                "trace_id": trace_id,
                "memory_context": memory_result.memory_context,
                "turn_count": memory_result.turn_count,
                "intent": triage_result.intent,
                "priority": triage_result.priority,
                "initial_risk": triage_result.risk,
                "retrieval_query": planning_result.rewritten_query,
                "sub_queries": planning_result.sub_queries,
                "citations": grounding_result.citations,
                "violations": compliance_result.violations,
                "risk_reason": risk_result.reason,
            }

        response = QueryResponse(
            answer=final_answer,
            confidence=verification_result.confidence,
            rationale=verification_result.rationale,
            escalation=escalation_result.escalation,
            followups=draft_result.followups,
            evidence=evidence_items,
            verifier={
                "ok": verification_result.ok,
                "confidence": verification_result.confidence,
                "rationale": verification_result.rationale,
                "unsupported_claims": verification_result.unsupported_claims,
                "grounded": grounding_result.grounded,
                "citations": grounding_result.citations,
            },
            quality=quality,
            action={
                "type": action_result.action_type,
                "note": action_result.note,
            },
            debug=debug,
        )

        self._audit(
            trace_id,
            "response_finalized",
            {
                "confidence": verification_result.confidence,
                "risk": risk_result.risk,
                "escalated": escalation_result.needs_escalation,
                "action_type": action_result.action_type,
            },
        )

        return response