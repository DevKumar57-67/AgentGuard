"""Compatibility exports for the original policy engine import path."""

from backend.services.policy_service import evaluate_policy


def evaluate_tool(tool: str) -> dict[str, str]:
    return evaluate_policy(tool)


__all__ = ["evaluate_policy", "evaluate_tool"]