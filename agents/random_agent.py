from __future__ import annotations
import random
from typing import Any, Dict

ACTIONS = ["read_policy", "inspect_schema", "query_case", "query_record", "request_approval", "call_api", "send_response", "write_audit_log", "finish"]


def random_agent(observation: Dict[str, Any]) -> Dict[str, Any]:
    action = random.choice(ACTIONS)
    payload = {}
    if action == "read_policy":
        payload = {"version": random.choice(["old", "current"])}
    elif action == "request_approval":
        payload = {"approver": random.choice(["manager", "finance", "security"])}
    elif action == "call_api":
        payload = {"refund_amount": 1000, "reason": "late_delivery"}
    elif action == "write_audit_log":
        payload = {"summary": "Random audit."}
    elif action == "send_response":
        payload = {"message": "Done."}
    return {"action_type": action, "payload": payload}
