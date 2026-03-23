import re
from typing import Any


SENSITIVE_DATA_PATTERNS = {
    "password": [
        r"\bpassword\b",
        r"\bpasscode\b",
    ],
    "ssn": [
        r"\bssn\b",
        r"\bsocial security\b",
        r"\bsocial security number\b",
        r"\b\d{3}-\d{2}-\d{4}\b",
    ],
    "cvv": [
        r"\bcvv\b",
        r"\bcvc\b",
        r"\bsecurity code\b",
    ],
    "credit_card": [
        r"\bcredit card\b",
        r"\bdebit card\b",
        r"\bcard number\b",
        r"\b\d{13,19}\b",
    ],
}

DISCLOSURE_PATTERNS = [
    r"\bmy\b",
    r"\bhere is\b",
    r"\bi can send\b",
    r"\bcan i send\b",
    r"\bi want to send\b",
    r"\bsend you\b",
    r"\bshare\b",
    r"\bsharing\b",
    r"\bgive you\b",
    r"\bprovide\b",
    r"\bprovided below\b",
    r"\bit is\b",
]

POLICY_QUESTION_PATTERNS = [
    r"\bcan an agent\b",
    r"\bshould an agent\b",
    r"\bwhat should an agent do\b",
    r"\bis it allowed\b",
    r"\bare agents allowed\b",
    r"\bwhat is the policy\b",
    r"\bwhat should happen if\b",
    r"\bhow should an agent handle\b",
]


def _normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _matches_any(patterns: list[str], text: str) -> bool:
    for pattern in patterns:
        if re.search(pattern, text):
            return True
    return False


def _detect_sensitive_categories(text: str) -> list[str]:
    found: list[str] = []

    for label, patterns in SENSITIVE_DATA_PATTERNS.items():
        if _matches_any(patterns, text):
            found.append(label)

    return found


def safety_tool(user_message: str) -> dict[str, Any]:
    """
    Detect whether the user is attempting to share or request processing
    of sensitive data in chat. Policy questions should not be blocked.
    """
    if not isinstance(user_message, str):
        raise ValueError("user_message must be a string")

    if not user_message.strip():
        raise ValueError("user_message cannot be empty")

    normalized = _normalize_text(user_message)

    sensitive_categories = _detect_sensitive_categories(normalized)
    has_sensitive_data = len(sensitive_categories) > 0
    looks_like_policy_question = _matches_any(POLICY_QUESTION_PATTERNS, normalized)
    looks_like_disclosure = _matches_any(DISCLOSURE_PATTERNS, normalized)

    blocked = False

    if has_sensitive_data and not looks_like_policy_question:
        if looks_like_disclosure:
            blocked = True
        elif re.search(r"\b\d{3}-\d{2}-\d{4}\b", normalized):
            blocked = True
        elif re.search(r"\b\d{13,19}\b", normalized):
            blocked = True

    if blocked:
        safe_response = (
            "I cannot process sensitive personal or payment data in chat. "
            "Please use a secure verified support channel."
        )
    else:
        safe_response = ""

    return {
        "blocked": blocked,
        "violations": sensitive_categories,
        "safe_response": safe_response,
        "policy_question": looks_like_policy_question,
    }
