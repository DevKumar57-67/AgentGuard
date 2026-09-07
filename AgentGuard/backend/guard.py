from .models import ToolCall
from .policy_engine import evaluate_tool
from .logger import log_event


def inspect_tool_call(tool_call: ToolCall):
    """
    Main AgentGuard inspection pipeline.

    Every agent tool request passes through this function
    before the actual tool is executed.
    """

    policy_result = evaluate_tool(tool_call.tool)

    result = {
        "agent_id": tool_call.agent_id,
        "tool": tool_call.tool,
        "arguments": tool_call.arguments,
        "risk": policy_result["risk"],
        "decision": policy_result["decision"],
        "reason": policy_result["reason"],
    }

    log_event(result.copy())

    return result