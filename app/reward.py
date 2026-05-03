from __future__ import annotations
from typing import Any, Dict, List, Tuple


def _deprecated_used(task: Dict[str, Any], payload: Dict[str, Any]) -> List[str]:
    deprecated = set(task.get("deprecated_fields", []))
    used = []
    def walk(obj: Any):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in deprecated:
                    used.append(key)
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)
    walk(payload)
    return sorted(set(used))


def validate_payload(task: Dict[str, Any], payload: Dict[str, Any], approvals: List[str]) -> Tuple[bool, str]:
    used_deprecated = _deprecated_used(task, payload)
    if used_deprecated:
        return False, f"Deprecated API fields used: {used_deprecated}"

    required = set(task.get("required_approvals", []))
    if not required.issubset(set(approvals)):
        return False, f"Missing approvals: {sorted(required - set(approvals))}"

    workflow = task["workflow"]
    expected = task["expected_payload"]

    if workflow == "refund_request":
        if payload.get("adjustment") != expected["adjustment"]:
            return False, "Invalid adjustment object for refund_request."
        if expected.get("approval_id") and not payload.get("approval_id"):
            return False, "approval_id required for refund."
        return True, "Refund API accepted."

    if workflow == "vendor_onboarding":
        if payload.get("vendor") != expected["vendor"]:
            return False, "Invalid nested vendor object."
        if payload.get("annual_spend") != expected["annual_spend"]:
            return False, "Invalid annual_spend."
        if set(payload.get("approvals", [])) != set(expected["approvals"]):
            return False, "Invalid approvals list."
        return True, "Vendor API accepted."

    if workflow == "privacy_deletion":
        if payload.get("subject_id") != expected["subject_id"]:
            return False, "Invalid subject_id."
        if sorted(payload.get("scope", [])) != sorted(expected["scope"]):
            return False, "Invalid privacy scope."
        if payload.get("redaction_mode") != expected["redaction_mode"]:
            return False, "Invalid redaction_mode."
        return True, "Privacy API accepted."

    if workflow == "billing_dispute":
        if payload.get("invoice_adjustment") != expected["invoice_adjustment"]:
            return False, "Invalid invoice_adjustment."
        if expected.get("approval_id") and not payload.get("approval_id"):
            return False, "approval_id required for billing dispute."
        return True, "Invoice API accepted."

    return False, "Unknown workflow."


def final_score(task: Dict[str, Any], flags: Dict[str, Any], steps: int) -> Tuple[float, Dict[str, Any]]:
    info = {
        "workflow_completed": False,
        "policy_adapted": bool(flags.get("current_policy_read")),
        "schema_adapted": bool(flags.get("schema_inspected")),
        "approval_correct": set(task.get("required_approvals", [])).issubset(set(flags.get("approvals", []))),
        "api_success": bool(flags.get("api_success")),
        "audit_complete": bool(flags.get("audit_written")),
        "response_sent": bool(flags.get("response_sent")),
        "sla_met": steps <= task.get("sla_steps", 999),
        "compliance_safe": bool(flags.get("audit_written")) if task.get("audit_required") else True,
    }
    completed = all([info["policy_adapted"], info["schema_adapted"], info["approval_correct"], info["api_success"], info["audit_complete"], info["response_sent"]])
    info["workflow_completed"] = completed
    reward = 0.0
    reward += 20 if completed else -15
    reward += 4 if info["sla_met"] else -6
    reward += 4 if info["policy_adapted"] else -4
    reward += 4 if info["schema_adapted"] else -4
    reward += 4 if info["approval_correct"] else -8
    reward += 4 if info["compliance_safe"] else -8
    reward += 2 if info["response_sent"] else -2
    return reward, info
