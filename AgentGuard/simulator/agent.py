import requests
import json


AGENTGUARD_URL = "http://127.0.0.1:8000/guard"


def call_agentguard(tool, arguments=None):
    """
    Send a simulated AI agent tool call to AgentGuard.
    """

    payload = {
        "agent_id": "demo-agent",
        "tool": tool,
        "arguments": arguments or {}
    }

    print("\n" + "=" * 60)

    print("AI AGENT REQUEST")
    print("=" * 60)

    print(json.dumps(payload, indent=4))

    try:
        response = requests.post(
            AGENTGUARD_URL,
            json=payload,
            timeout=5
        )

        response.raise_for_status()

        result = response.json()

        print("\nAGENTGUARD DECISION")
        print("=" * 60)

        print(json.dumps(result, indent=4))

        print("\nRESULT")
        print("=" * 60)

        if result["decision"] == "ALLOW":
            print("✅ ALLOWED")

        elif result["decision"] == "APPROVAL_REQUIRED":
            print("⚠️ APPROVAL REQUIRED")

        elif result["decision"] == "BLOCK":
            print("🚫 BLOCKED")

        return result

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to AgentGuard.")
        print("Make sure the FastAPI server is running.")

    except requests.exceptions.RequestException as error:
        print(f"❌ Request failed: {error}")


if __name__ == "__main__":

    # Safe operation
    call_agentguard(
        "search_web",
        {
            "query": "latest AI security research"
        }
    )

    # Sensitive operation
    call_agentguard(
        "send_email",
        {
            "to": "user@example.com",
            "subject": "Test",
            "message": "This is a test."
        }
    )

    # Dangerous operation
    call_agentguard(
        "execute_shell",
        {
            "command": "rm -rf important_data"
        }
    )

    # Unknown operation
    call_agentguard(
        "unknown_tool",
        {
            "data": "test"
        }
    )