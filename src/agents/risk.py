from dataclasses import dataclass
import re

@dataclass
class RiskResult:
    risk: str
    reason: str

@dataclass
class RiskTopicRule:
    label: str
    phrases: list[str]


class RiskAgent:

    RISK_TOPIC_RULES = (RiskTopicRule("litigation", ["lawsuit", "litigation", "sued", "class action", "court case"]),
                        RiskTopicRule("regulatory", ["regulator", "regulatory", "fine", "penalty", "compliance review"]),
                        RiskTopicRule("sanctions", ["sanction", "sanctions", "ofac", "restricted party", "blacklisted"]),
                        RiskTopicRule("fraud", ["fraud", "fraudulent", "embezzlement", "bribery", "money laundering"]))

    def _check_type(self, data, data_name: str, data_type: type) -> None:
        if not isinstance(data, data_type):
            raise TypeError(f"{data_name} is not {data_type}")  
    
    def _normalize(self, query_text:str) -> str:
        query_text = query_text.lower()
        query_text = query_text.strip()
        query_text = re.sub("[^\w\s]", " ", query_text)
        query_text = re.sub("\s+", " ", query_text)
        query_text = query_text.strip()

        return query_text

    
    def _match_risk_rules(self, query_text: str) -> list[str]:
        matched_labels = set()

        for rule in self.RISK_TOPIC_RULES:
            for phrase in rule.phrases:
                pattern = rf"\b{re.escape(phrase)}\b"
                if re.search(pattern, query_text):
                    matched_labels.add(rule.label)

        return list(matched_labels)
        
    def run(self, query_text: str, verification_ok: bool, compliance_ok: bool) -> RiskResult:

        self._check_type(query_text, "query_text", str)
        self._check_type(verification_ok, "verification_ok", bool)
        self._check_type(compliance_ok, "compliance_ok", bool)

        query_text = self._normalize(query_text)
        matched_labels = self._match_risk_rules(query_text)

        if not compliance_ok:
            risk = "high"
            reason = "Compliance check failed."
            return RiskResult(risk, reason)
        
        if not verification_ok:
            risk = "high"
            reason = "Verification check failed."
            return RiskResult(risk, reason)
        
        high_risk_labels = ["litigation", "sanctions", "fraud"]
        for label in high_risk_labels:
            if label in matched_labels:
                risk = "high"
                reason = f"Matched high-risk topic label: {label}."
                return RiskResult(risk, reason)
        
        if "regulatory" in matched_labels:
            risk = "medium"
            reason = "Compliance topic requires caution."  
            return RiskResult(risk, reason) 

        risk = "low"
        reason = "No high-risk signals detected."

        return RiskResult(risk, reason)
