from __future__ import annotations
from typing import Any, Dict


def public_case_view(task: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "case_id": task["case_id"],
        "workflow": task["workflow"],
        "user_request": task["user_request"],
        "sla_steps": task["sla_steps"],
        "visible_hint": "Policy/API/compliance rules may have changed. Inspect before acting.",
    }


def policy_view(task: Dict[str, Any], version: str = "current") -> str:
    return task["old_policy"] if version == "old" else task["current_policy"]


def schema_view(task: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema_name": task["schema_name"],
        "deprecated_fields": task["deprecated_fields"],
        "expected_payload_hint": task["expected_payload"],
        "warning": "Deprecated fields are rejected and penalized.",
    }


def record_view(task: Dict[str, Any]) -> Dict[str, Any]:
    keys = ["record_id", "subject_id", "amount", "reason", "vendor_name", "annual_spend", "risk_tier", "region"]
    return {k: task[k] for k in keys if k in task}
