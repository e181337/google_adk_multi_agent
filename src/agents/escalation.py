from dataclasses import dataclass

@dataclass
class EscalationResult:
    needs_escalation: bool
    escalation: str | None

class EscalationHandoffAgent:

    RISK = {"low", "medium", "high"}

    def _check_type(self, data, data_name: str, data_type: type) -> None:
        if not isinstance(data, data_type):
            raise TypeError(f"{data_name} is not {data_type}") 
    
    def _risk_validation(self, risk: str) -> None:
        if  risk not in self.RISK:
            raise ValueError(f"Invalid risk value {risk}")

    def run(self, risk: str, verification_ok: bool, compliance_ok: bool, query_text: str) -> EscalationResult:

        self._check_type(risk, "risk", str)
        self._check_type(verification_ok, "verification_ok", bool)
        self._check_type(compliance_ok, "compliance_ok", bool)
        self._check_type(query_text, "query_text", str)

        self._risk_validation(risk)

        if not compliance_ok:
            needs_escalation = True
            escalation = "Escalate to compliance specialist due to policy risk."
        
        elif not verification_ok:
            needs_escalation = True
            escalation = "Escalate due to verification failure."   

        elif risk == "high":
            needs_escalation = True
            escalation = "Escalate due to high-risk topic."
        
        else:
            needs_escalation = False
            escalation = None

        return EscalationResult(needs_escalation, escalation)
        

