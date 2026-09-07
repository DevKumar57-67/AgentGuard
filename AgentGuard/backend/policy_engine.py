import re

def evaluate_policy(tool: str, prompt: str = "") -> dict:
    """
    Evaluates tool calls and prompts against security policy rules.
    Categories: GREEN (ALLOW), AMBER (APPROVAL_REQUIRED), RED (BLOCK)
    """
    prompt_lower = prompt.lower()
    
    # Bonus Feature: Prompt Injection & Destructive Pattern Detection
    injection_patterns = [
        r"drop\s+database", r"rm\s+-rf", r"sudo", r"ignore\s+previous\s+instructions",
        r"dump\s+passwords", r"eval\(", r"exec\("
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, prompt_lower):
            return {
                "risk": "RED",
                "decision": "BLOCK",
                "reason": f"Prompt injection / destructive command detected: '{pattern}'"
            }

    # Tool-level Policy Enforcement
    if tool in ["search_web", "read_docs", "get_weather"]:
        return {
            "risk": "GREEN",
            "decision": "ALLOW",
            "reason": "Low-risk read-only operation."
        }
    elif tool in ["send_email", "write_database", "post_tweet"]:
        return {
            "risk": "AMBER",
            "decision": "APPROVAL_REQUIRED",
            "reason": "This operation affects an external system or user state."
        }
    elif tool in ["execute_shell", "drop_database_table", "delete_file"]:
        return {
            "risk": "RED",
            "decision": "BLOCK",
            "reason": "Potentially destructive or highly sensitive system-level operation."
        }
    else:
        return {
            "risk": "AMBER",
            "decision": "APPROVAL_REQUIRED",
            "reason": "Unrecognized tool call defaults to Amber human approval."
        }