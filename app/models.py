from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field

ActionType = Literal[
    "read_policy",
    "inspect_schema",
    "query_case",
    "query_record",
    "request_approval",
    "call_api",
    "send_response",
    "write_audit_log",
    "finish",
]

class ActionRequest(BaseModel):
    action_type: ActionType
    target: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)

class StepResponse(BaseModel):
    observation: Dict[str, Any]
    reward: float
    done: bool
    info: Dict[str, Any]
