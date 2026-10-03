from typing import TypedDict


class RiskAssessment(TypedDict):
    risk: str
    decision: str
    reason: str


LOW_RISK_TOOLS = frozenset({"search_web", "read_docs", "get_weather"})
APPROVAL_TOOLS = frozenset({"send_email", "write_database", "post_tweet"})
BLOCKED_TOOLS = frozenset({"execute_shell", "drop_database_table", "delete_file"})


def assess_tool_risk(tool: str) -> RiskAssessment:
    if tool in LOW_RISK_TOOLS:
        return {
            "risk": "GREEN",
            "decision": "ALLOW",
            "reason": "Low-risk read-only operation.",
        }
    if tool in APPROVAL_TOOLS:
        return {
            "risk": "AMBER",
            "decision": "APPROVAL_REQUIRED",
            "reason": "This operation affects an external system or user state.",
        }
    if tool in BLOCKED_TOOLS:
        return {
            "risk": "RED",
            "decision": "BLOCK",
            "reason": "Potentially destructive or highly sensitive system-level operation.",
        }
    return {
        "risk": "AMBER",
        "decision": "APPROVAL_REQUIRED",
        "reason": "Unrecognized tool call defaults to Amber human approval.",
    }