from dataclasses import dataclass

@dataclass
class  AuditEvent:
    trace_id: str
    stage: str
    payload: dict

@dataclass
class AuditResult:
    event: AuditEvent

class AuditObservabilityAgent:

    def __init__(self):
        self.events: list[AuditEvent] = []

    def _check_type(self, data, data_name: str, data_type: type) -> None:
        if not isinstance(data, data_type):
            raise TypeError(f"{data_name} is not {data_type}")
    
    def _check_str_empty(self, data:str, data_name: str) -> None:
        if data.strip() == "":
            raise ValueError(f"empty string at {data_name}")
    
    def list_events(self, trace_id: str | None = None) ->  list[AuditEvent]:

        if trace_id is None:
            return self.events
        
        filtered_events = []
        for event in self.events:
            if event.trace_id == trace_id:
                filtered_events.append(event)
        
        return filtered_events
                
    def _validation(self, trace_id: str, stage: str, payload: dict) -> None:

        self._check_type(trace_id, "trace_id", str)
        self._check_str_empty(trace_id, "trace_id")

        self._check_type(stage, "stage", str)
        self._check_str_empty(stage, "stage")

        self._check_type(payload, "payload", dict)
    
    def run(self, trace_id: str, stage: str, payload: dict) -> AuditResult:

        self._validation(trace_id, stage, payload)

        audit_event = AuditEvent(trace_id, stage, payload)
        self.events.append(audit_event)
        result = AuditResult(audit_event)

        return result


