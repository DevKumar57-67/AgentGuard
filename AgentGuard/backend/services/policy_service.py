from backend.core.prompt_injection_detector import detect_prompt_injection
from backend.core.risk_engine import RiskAssessment, assess_tool_risk


def evaluate_policy(tool: str, prompt: str = "") -> RiskAssessment:
    injection_pattern = detect_prompt_injection(prompt)
    if injection_pattern is not None:
        return {
            "risk": "RED",
            "decision": "BLOCK",
            "reason": f"Prompt injection / destructive command detected: '{injection_pattern}'",
        }
    return assess_tool_risk(tool)