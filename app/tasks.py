from __future__ import annotations

import random
from typing import Any, Dict, List


def _refund_case(idx: int, rng: random.Random) -> Dict[str, Any]:
    amount = rng.choice([1200, 1800, 2400, 3200, 4500, 7200])
    requires_approval = amount > 2000
    reason = rng.choice(["late_delivery", "damaged_item", "duplicate_charge"])
    return {
        "id": f"REF-{idx:04d}",
        "workflow": "refund_request",
        "user_request": f"Customer asks for refund of INR {amount} because of {reason}.",
        "case_id": f"CASE-REF-{idx:04d}",
        "record_id": f"ORD-{idx:04d}",
        "amount": amount,
        "reason": reason,
        "sla_steps": rng.choice([7, 8, 9]),
        "old_policy": "refund_policy_v1: refunds below INR 5000 can be issued automatically.",
        "current_policy": "refund_policy_v2: refunds above INR 2000 require manager approval and audit log.",
        "schema_name": "billing_api_v2",
        "deprecated_fields": ["refund_amount", "reason"],
        "requires_approval": requires_approval,
        "required_approvals": ["manager"] if requires_approval else [],
        "compliance_rule": "audit_required_for_all_refunds",
        "audit_required": True,
        "expected_payload": {
            "adjustment": {"amount": amount, "policy_code": "SHIP_DELAY"},
            "approval_id": "manager-approved" if requires_approval else None,
        },
    }


def _vendor_case(idx: int, rng: random.Random) -> Dict[str, Any]:
    spend = rng.choice([8000, 15000, 30000, 45000, 90000])
    risk = rng.choice(["low", "medium", "high"])
    approvals = []
    if spend >= 25000:
        approvals.append("finance")
    if risk == "high":
        approvals.append("security")
    return {
        "id": f"VEN-{idx:04d}",
        "workflow": "vendor_onboarding",
        "user_request": f"Business team wants to onboard vendor ACME-{idx} with annual spend INR {spend} and {risk} risk.",
        "case_id": f"CASE-VEN-{idx:04d}",
        "record_id": f"VENDOR-{idx:04d}",
        "vendor_name": f"ACME-{idx}",
        "annual_spend": spend,
        "risk_tier": risk,
        "sla_steps": rng.choice([8, 9, 10]),
        "old_policy": "vendor_policy_v1: finance approval required only above INR 50000.",
        "current_policy": "vendor_policy_v2: finance approval required above INR 25000; security approval required for high-risk vendors.",
        "schema_name": "vendor_api_v2",
        "deprecated_fields": ["vendor_name", "spend", "risk"],
        "requires_approval": bool(approvals),
        "required_approvals": approvals,
        "compliance_rule": "vendor_audit_and_risk_attestation_required",
        "audit_required": True,
        "expected_payload": {
            "vendor": {"name": f"ACME-{idx}", "risk_tier": risk},
            "annual_spend": spend,
            "approvals": approvals,
        },
    }


def _privacy_case(idx: int, rng: random.Random) -> Dict[str, Any]:
    region = rng.choice(["EU", "India", "California"])
    return {
        "id": f"PRI-{idx:04d}",
        "workflow": "privacy_deletion",
        "user_request": f"User requests deletion/redaction of personal data. Region: {region}.",
        "case_id": f"CASE-PRI-{idx:04d}",
        "record_id": f"USER-{idx:04d}",
        "subject_id": f"USER-{idx:04d}",
        "region": region,
        "sla_steps": rng.choice([6, 7, 8]),
        "old_policy": "privacy_policy_v1: delete CRM record and close ticket.",
        "current_policy": "privacy_policy_v2: redact CRM and analytics data, retain audit proof, and send confirmation.",
        "schema_name": "privacy_api_v2",
        "deprecated_fields": ["delete_everything", "manual_delete"],
        "requires_approval": False,
        "required_approvals": [],
        "compliance_rule": "retain_audit_proof_after_redaction",
        "audit_required": True,
        "expected_payload": {
            "subject_id": f"USER-{idx:04d}",
            "scope": ["crm", "analytics"],
            "redaction_mode": "retain_audit",
        },
    }


def _billing_case(idx: int, rng: random.Random) -> Dict[str, Any]:
    amount = rng.choice([900, 1500, 2600, 5400])
    requires_approval = amount > 2500
    return {
        "id": f"BIL-{idx:04d}",
        "workflow": "billing_dispute",
        "user_request": f"Customer disputes duplicate invoice charge of INR {amount}.",
        "case_id": f"CASE-BIL-{idx:04d}",
        "record_id": f"INV-{idx:04d}",
        "amount": amount,
        "sla_steps": rng.choice([7, 8, 9]),
        "old_policy": "billing_policy_v1: reverse duplicate invoices below INR 5000 automatically.",
        "current_policy": "billing_policy_v2: disputes above INR 2500 require finance approval and audit memo.",
        "schema_name": "invoice_api_v2",
        "deprecated_fields": ["chargeback_amount", "invoice_reason"],
        "requires_approval": requires_approval,
        "required_approvals": ["finance"] if requires_approval else [],
        "compliance_rule": "billing_adjustment_audit_memo_required",
        "audit_required": True,
        "expected_payload": {
            "invoice_adjustment": {"amount": amount, "reason_code": "DUPLICATE_INVOICE"},
            "approval_id": "finance-approved" if requires_approval else None,
        },
    }


def load_tasks(n: int = 120, seed: int = 42) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    builders = [_refund_case, _vendor_case, _privacy_case, _billing_case]
    tasks: List[Dict[str, Any]] = []
    for idx in range(1, n + 1):
        tasks.append(builders[(idx - 1) % len(builders)](idx, rng))
    rng.shuffle(tasks)
    return tasks
