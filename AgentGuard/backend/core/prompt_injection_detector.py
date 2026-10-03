import re

INJECTION_PATTERNS = (
    r"drop\s+database",
    r"rm\s+-rf",
    r"sudo",
    r"ignore\s+previous\s+instructions",
    r"dump\s+passwords",
    r"eval\(",
    r"exec\(",
)


def detect_prompt_injection(text: str) -> str | None:
    normalized_text = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, normalized_text):
            return pattern
    return None