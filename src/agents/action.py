from dataclasses import dataclass

@dataclass
class ActionResult:

    action_type: str
    note: str

class ActionWorkflowAgent:

    ALLOWED_INTENTS = {"billing", "technical_support", "account", "compliance", "general"}
    ALLOWED_PRIORITIES = {"low", "medium", "high"}

    def _check_type(self, data, data_name: str, data_type: type) -> None:
        if not isinstance(data, data_type):
            raise TypeError(f"{data_name} is not {data_type}")  

    def _validate(self, intent: str, priority: str, compliance_ok: bool):
        
        self._check_type(intent, "intent", str)
        self._check_type(priority, "priority", str)
        self._check_type(compliance_ok, "compliance_ok", bool)

        if not intent in self.ALLOWED_INTENTS:
            raise ValueError("Invalid intent")
        
        if not priority in self.ALLOWED_PRIORITIES:
            raise ValueError("Invalid priority")

    def run(self, intent: str, priority: str, compliance_ok: bool) -> ActionResult:


        self._validate(intent, priority, compliance_ok)

        if not compliance_ok:
            action_type = "secure_channel_required"
            note = "Sensitive information detected. Use secure verified channel."
        
        elif intent == "billing":
            action_type = "open_billing_ticket"
            note = "Billing request routed to billing workflow."

        elif intent == "technical_support":
            action_type = "route_technical_queue"
            note = "Technical support request routed to technical queue."     

        elif intent == "account":
            action_type = "route_account_support" 
            note = "Account-related request routed to account support." 

        elif intent == "compliance":
            action_type = "route_compliance_queue"
            note = "Compliance request routed to compliance queue."
        
        else:
            action_type = "none"
            note = "No specialized workflow required."
        
        return ActionResult(action_type, note)