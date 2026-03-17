from dataclasses import dataclass
import re

@dataclass
class ComplianceResult:
    compliance_ok: bool
    safe_answer: str
    violations: list[str]

@dataclass
class ViolationRule:
    label: str
    keywords: list[str]
    patterns: list[str]    

class CompliancePolicyAgent:

    RULES = [ViolationRule("ssn", 
                        ["ssn", "social security", "social security number"], 
                        [r"\b\d{3}-\d{2}-\d{4}\b"]),
             ViolationRule("payment_card", 
                        ["credit card", "card number", "debit card"], 
                        [r"\b\d{13,19}\b"]),
             ViolationRule("cvv", 
                        ["cvv", "cvc", "security code"], 
                        []),
            ViolationRule("password", 
                        ["password", "my password is", "passcode"], 
                        [])]
    
        
    def _check_type(self, data, data_name: str, data_type: type) -> None:
        if not isinstance(data, data_type):
            raise TypeError(f"{data_name} is not {data_type}")
        
    def _keyword_match(self, query_text:str, draft_text:str) -> list:
        violations_set = set()
        for rule in self.RULES:
            for value in rule.keywords:
                if re.search(rf"\b{re.escape(value)}\b", query_text) or re.search(rf"\b{re.escape(value)}\b", draft_text):
                    if rule.label not in violations_set:
                        violations_set.add(rule.label)
                    
        violations = list(violations_set)
        return violations
    
    def _normalize_function(self, text:str) -> str:
        text = text.lower()
        text = text.replace("-", " ")
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s]", "", text) 
        text = text.strip()
        return text

    
    def _normalize(self, query_text:str, draft_text:str) -> tuple[str, str]:
        query_text = self._normalize_function(query_text)
        draft_text = self._normalize_function(draft_text)

        return query_text, draft_text
    
    def _pattern_match(self, text:str, pattern:str) -> bool:
        if re.search(pattern, text):
            result = True
        else:
            result = False
        
        return result
    
    def _pattern_check(self, query_text:str, draft_text:str) -> tuple[list, list]:
        violation_query_text = set()
        violation_draft_text = set()
        for rule in self.RULES:
            for pattern in rule.patterns:
                pattern_query_text = self._pattern_match(query_text, pattern)
                pattern_draft_text = self._pattern_match(draft_text,pattern)
                if pattern_query_text:
                    violation_query_text.add(rule.label)   
                if pattern_draft_text:
                    violation_draft_text.add(rule.label)    

        return   list(violation_query_text), list(violation_draft_text)
    
    def run(self, query_text:str, draft_text:str) -> ComplianceResult:

        self._check_type(query_text, "query_text", str)
        self._check_type(draft_text, "draft_text", str)
        
        query_text_normalize, draft_text_normalize = self._normalize(query_text, draft_text)

        violation_pattern_query, violation_pattern_draft = self._pattern_check(query_text, draft_text)

        violations_keyword = self._keyword_match(query_text_normalize, draft_text_normalize)
        violations = list(set(violation_pattern_query) | set(violation_pattern_draft) | set(violations_keyword))

        if violations: 
            compliance_ok = False
            safe_answer = "I cannot process sensitive personal data in chat. Please use secure verified channels."
        else: 
            compliance_ok = True
            safe_answer = draft_text

        return ComplianceResult(compliance_ok, safe_answer, violations)