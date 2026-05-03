from __future__ import annotations
from typing import Any, Dict, List


def _required_approvals(obs: Dict[str, Any]) -> List[str]:
    details = obs["visible"].get("case_details") or {}
    return details.get("required_approvals", [])


def _current_approvals(obs: Dict[str, Any]) -> List[str]:
    return obs["flags"].get("approvals", [])


def _payload(obs: Dict[str, Any]) -> Dict[str, Any]:
    visible = obs["visible"]
    workflow = visible["workflow"]
    record = visible.get("known_record") or {}
    approvals = _current_approvals(obs)
    if workflow == "refund_request":
        amount = record.get("amount")
        payload = {"adjustment": {"amount": amount, "policy_code": "SHIP_DELAY"}}
        if "manager" in approvals:
            payload["approval_id"] = "manager-approved"
        return payload
    if workflow == "vendor_onboarding":
        return {"vendor": {"name": record.get("vendor_name"), "risk_tier": record.get("risk_tier")}, "annual_spend": record.get("annual_spend"), "approvals": approvals}
    if workflow == "privacy_deletion":
        return {"subject_id": record.get("subject_id"), "scope": ["crm", "analytics"], "redaction_mode": "retain_audit"}
    if workflow == "billing_dispute":
        amount = record.get("amount")
        payload = {"invoice_adjustment": {"amount": amount, "reason_code": "DUPLICATE_INVOICE"}}
        if "finance" in approvals:
            payload["approval_id"] = "finance-approved"
        return payload
    return {}


def rule_based_agent(observation: Dict[str, Any]) -> Dict[str, Any]:
    flags = observation["flags"]
    if not flags["current_policy_read"]:
        return {"action_type": "read_policy", "payload": {"version": "current"}}
    if not flags["schema_inspected"]:
        return {"action_type": "inspect_schema", "payload": {}}
    if not flags["case_queried"]:
        return {"action_type": "query_case", "payload": {}}
    if not flags["record_queried"]:
        return {"action_type": "query_record", "payload": {}}
    for approver in _required_approvals(observation):
        if approver not in _current_approvals(observation):
            return {"action_type": "request_approval", "target": approver, "payload": {"approver": approver}}
    if not flags["api_success"]:
        return {"action_type": "call_api", "payload": _payload(observation)}
    if not flags["audit_written"]:
        return {"action_type": "write_audit_log", "payload": {"summary": "Completed using current policy and schema."}}
    if not flags["response_sent"]:
        return {"action_type": "send_response", "payload": {"message": "Your request was processed according to current policy."}}
    return {"action_type": "finish", "payload": {}}
