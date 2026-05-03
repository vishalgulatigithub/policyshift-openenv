from __future__ import annotations
from typing import Any, Dict


def stale_policy_agent(observation: Dict[str, Any]) -> Dict[str, Any]:
    flags = observation["flags"]
    if not flags["old_policy_read"]:
        return {"action_type": "read_policy", "payload": {"version": "old"}}
    if not flags["record_queried"]:
        return {"action_type": "query_record", "payload": {}}
    if not flags["api_success"]:
        return {"action_type": "call_api", "payload": {"refund_amount": 1000, "reason": "late_delivery", "vendor_name": "UNKNOWN", "spend": 1000, "delete_everything": True, "chargeback_amount": 1000}}
    return {"action_type": "finish", "payload": {}}
