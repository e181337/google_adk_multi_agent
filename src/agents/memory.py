from dataclasses import dataclass
@dataclass
class MemoryResult:
    memory_context: str
    turn_count: int

class ConversationMemoryAgent:

    def __init__(self):
        self.sessions: dict[str, list[str]] = {}

    def _check_type(self, data, data_name: str, data_type: type) -> None:
        if not isinstance(data, data_type):
            raise TypeError(f"{data_name} is not {data_type}")
        
        if isinstance(data, str):
            if data.strip() == "":
                raise ValueError(f"{data_name} is empty. string")

    def run(self, session_id: str, query_text: str) -> MemoryResult:

        self._check_type(session_id, "session_id", str)
        self._check_type(query_text, "query_text", str)

        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append(query_text)
        self.sessions[session_id] = self.sessions[session_id][-4:]
        memory_context = " | ".join(self.sessions[session_id])
        turn_count = len(self.sessions[session_id])

        return MemoryResult(memory_context, turn_count)
 
