from __future__ import annotations
from typing import Any, Dict
import numpy as np

ACTIONS = ["read_policy", "inspect_schema", "query_case", "query_record", "request_approval", "call_api", "send_response", "write_audit_log", "finish"]
WORKFLOWS = ["refund_request", "vendor_onboarding", "privacy_deletion", "billing_dispute"]


def encode_state(obs: Dict[str, Any]) -> np.ndarray:
    visible = obs["visible"]
    flags = obs["flags"]
    vec = []
    workflow = visible.get("workflow")
    vec.extend([1.0 if workflow == w else 0.0 for w in WORKFLOWS])
    bool_keys = ["old_policy_read", "current_policy_read", "schema_inspected", "case_queried", "record_queried", "api_success", "audit_written", "response_sent"]
    vec.extend([1.0 if flags.get(k) else 0.0 for k in bool_keys])
    steps = float(obs.get("steps", 0))
    max_steps = max(float(obs.get("max_steps", 12)), 1.0)
    sla_steps = float(visible.get("sla_steps", max_steps))
    vec.append(steps / max_steps)
    vec.append(max((sla_steps - steps) / max_steps, 0.0))
    vec.append(len(flags.get("approvals", [])) / 3.0)
    return np.array(vec, dtype=np.float32)


def action_index_to_dict(action_idx: int, obs: Dict[str, Any]) -> Dict[str, Any]:
    action = ACTIONS[action_idx]
    if action == "read_policy":
        return {"action_type": "read_policy", "payload": {"version": "current"}}
    if action == "request_approval":
        details = obs["visible"].get("case_details") or {}
        required = details.get("required_approvals", [])
        for approver in required:
            if approver not in obs["flags"].get("approvals", []):
                return {"action_type": "request_approval", "target": approver, "payload": {"approver": approver}}
        return {"action_type": "request_approval", "payload": {"approver": "manager"}}
    if action == "call_api":
        from agents.rule_based import _payload
        return {"action_type": "call_api", "payload": _payload(obs)}
    if action == "write_audit_log":
        return {"action_type": "write_audit_log", "payload": {"summary": "PolicyShift PPO audit trail."}}
    if action == "send_response":
        return {"action_type": "send_response", "payload": {"message": "Processed using current policy and schema."}}
    return {"action_type": action, "payload": {}}
