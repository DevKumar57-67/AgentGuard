POLICIES = {
    # Low-risk operations
    "search_web": "GREEN",
    "get_weather": "GREEN",
    "read_file": "GREEN",

    # Potentially sensitive operations
    "send_email": "AMBER",
    "send_message": "AMBER",
    "create_account": "AMBER",

    # Dangerous operations
    "delete_file": "RED",
    "execute_shell": "RED",
    "drop_database": "RED",
    "transfer_money": "RED",
}


def evaluate_tool(tool: str):

    risk = POLICIES.get(tool, "RED")

    if risk == "GREEN":
        return {
            "risk": "GREEN",
            "decision": "ALLOW",
            "reason": "Low-risk operation."
        }

    if risk == "AMBER":
        return {
            "risk": "AMBER",
            "decision": "APPROVAL_REQUIRED",
            "reason": "This operation can affect an external system or user."
        }

    return {
        "risk": "RED",
        "decision": "BLOCK",
        "reason": "Unknown or potentially destructive operation."
    }