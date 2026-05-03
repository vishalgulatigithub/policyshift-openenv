from __future__ import annotations
import random
from typing import Any, Dict, Optional
from app.models import ActionRequest
from app.reward import final_score, validate_payload
from app.tasks import load_tasks
from app.tools import policy_view, public_case_view, record_view, schema_view


class PolicyShiftEnv:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.tasks = load_tasks(seed=seed)
        self.current_task: Optional[Dict[str, Any]] = None
        self.steps = 0
        self.max_steps = 12
        self.total_reward = 0.0
        self.flags: Dict[str, Any] = {}
        self.visible: Dict[str, Any] = {}
        self.timeline = []

    def reset(self) -> Dict[str, Any]:
        self.current_task = self.rng.choice(self.tasks)
        self.steps = 0
        self.total_reward = 0.0
        self.timeline = []
        self.flags = {
            "old_policy_read": False,
            "current_policy_read": False,
            "schema_inspected": False,
            "case_queried": False,
            "record_queried": False,
            "approvals": [],
            "api_success": False,
            "audit_written": False,
            "response_sent": False,
            "finished": False,
        }
        self.visible = public_case_view(self.current_task)
        self.visible.update({
            "known_policy": None,
            "known_schema": None,
            "known_record": None,
            "case_details": None,
            "api_result": None,
            "audit_status": "missing",
            "timeline": [],
        })
        return self.observation()

    def observation(self) -> Dict[str, Any]:
        return {
            "visible": self.visible,
            "flags": self.flags,
            "steps": self.steps,
            "max_steps": self.max_steps,
            "total_reward": round(self.total_reward, 3),
            "available_actions": [
                "read_policy", "inspect_schema", "query_case", "query_record",
                "request_approval", "call_api", "send_response", "write_audit_log", "finish"
            ],
        }

    def get_state(self) -> Dict[str, Any]:
        return self.observation()

    def step(self, action: ActionRequest | Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(action, dict):
            action = ActionRequest(**action)
        if self.current_task is None:
            self.reset()
        assert self.current_task is not None
        self.steps += 1
        reward = -0.2
        done = False
        msg = ""

        if self.steps > self.current_task["sla_steps"]:
            reward -= 1.5
            msg += "SLA pressure penalty. "

        if action.action_type == "read_policy":
            version = action.payload.get("version", "current")
            if version == "old":
                self.flags["old_policy_read"] = True
                self.visible["known_policy"] = policy_view(self.current_task, "old")
                reward -= 1.0
                msg += "Old/stale policy read. "
            else:
                self.flags["current_policy_read"] = True
                self.visible["known_policy"] = policy_view(self.current_task, "current")
                reward += 2.0
                msg += "Current policy read. "

        elif action.action_type == "inspect_schema":
            self.flags["schema_inspected"] = True
            self.visible["known_schema"] = schema_view(self.current_task)
            reward += 2.0
            msg += "Current API schema inspected. "

        elif action.action_type == "query_case":
            self.flags["case_queried"] = True
            self.visible["case_details"] = {
                "workflow": self.current_task["workflow"],
                "requires_approval": self.current_task["requires_approval"],
                "required_approvals": self.current_task["required_approvals"],
                "compliance_rule": self.current_task["compliance_rule"],
                "audit_required": self.current_task["audit_required"],
            }
            reward += 1.2
            msg += "Case details queried. "

        elif action.action_type == "query_record":
            self.flags["record_queried"] = True
            self.visible["known_record"] = record_view(self.current_task)
            reward += 1.2
            msg += "Business record queried. "

        elif action.action_type == "request_approval":
            approver = action.payload.get("approver") or action.target
            required = self.current_task.get("required_approvals", [])
            if approver in required:
                if approver not in self.flags["approvals"]:
                    self.flags["approvals"].append(approver)
                reward += 2.5
                msg += f"Required approval granted: {approver}. "
            elif required:
                reward -= 2.0
                msg += f"Wrong approval requested: {approver}. Required: {required}. "
            else:
                reward -= 0.8
                msg += "Approval not required. "

        elif action.action_type == "call_api":
            if not self.flags["schema_inspected"]:
                reward -= 3.0
                msg += "API call rejected because schema was not inspected. "
                self.visible["api_result"] = msg
            else:
                ok, api_msg = validate_payload(self.current_task, action.payload, self.flags["approvals"])
                self.visible["api_result"] = api_msg
                if ok:
                    self.flags["api_success"] = True
                    reward += 5.0
                else:
                    reward -= 5.0
                msg += api_msg + " "

        elif action.action_type == "write_audit_log":
            summary = action.payload.get("summary", "")
            if summary and self.flags["api_success"]:
                self.flags["audit_written"] = True
                self.visible["audit_status"] = "complete"
                reward += 3.0
                msg += "Audit trail written. "
            else:
                reward -= 2.0
                msg += "Audit log incomplete or written before successful API action. "

        elif action.action_type == "send_response":
            if self.flags["api_success"] and self.flags["audit_written"]:
                self.flags["response_sent"] = True
                reward += 2.0
                msg += "User-safe response sent. "
            else:
                reward -= 2.0
                msg += "Response sent before safe workflow completion. "

        elif action.action_type == "finish":
            final_reward, final_info = final_score(self.current_task, self.flags, self.steps)
            reward += final_reward
            done = True
            self.flags["finished"] = True
            msg += "Episode finished. "
        else:
            reward -= 1.0
            msg += "Unknown action. "

        if self.steps >= self.max_steps:
            done = True
            msg += "Max steps reached. "

        event = {"step": self.steps, "action": action.action_type, "target": action.target, "payload": action.payload, "message": msg.strip(), "reward_delta": round(reward, 3)}
        if action.action_type == "finish":
            _, final_info = final_score(self.current_task, self.flags, self.steps)
            event["final_info"] = final_info
        self.total_reward += reward
        self.timeline.append(event)
        self.visible["timeline"] = self.timeline[-8:]
        return {"observation": self.observation(), "reward": round(reward, 3), "done": done, "info": {"event": event, "task_id": self.current_task["id"], "workflow": self.current_task["workflow"], "total_reward": round(self.total_reward, 3)}}
