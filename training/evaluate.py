from __future__ import annotations
from typing import Any, Callable, Dict
from agents.random_agent import random_agent
from agents.rule_based import rule_based_agent
from agents.stale_policy_agent import stale_policy_agent
from app.env import PolicyShiftEnv

AGENTS: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {"random": random_agent, "stale_policy": stale_policy_agent, "rule": rule_based_agent}


def evaluate_agent(agent_type: str, num_episodes: int = 25) -> Dict[str, Any]:
    if agent_type not in AGENTS:
        raise ValueError(f"Unknown agent_type={agent_type}. Choose from {list(AGENTS)}")
    env = PolicyShiftEnv(seed=123)
    agent_fn = AGENTS[agent_type]
    totals = {"reward": 0.0, "workflow_completed": 0, "policy_adapted": 0, "schema_adapted": 0, "approval_correct": 0, "api_success": 0, "audit_complete": 0, "sla_met": 0}
    samples = []
    for ep in range(num_episodes):
        obs = env.reset()
        done = False
        final_info = {}
        for _ in range(env.max_steps):
            action = agent_fn(obs)
            result = env.step(action)
            obs = result["observation"]
            done = result["done"]
            event = result["info"]["event"]
            if event.get("final_info"):
                final_info = event["final_info"]
            if done:
                break
        if not final_info:
            result = env.step({"action_type": "finish", "payload": {}})
            final_info = result["info"]["event"].get("final_info", {})
        totals["reward"] += env.total_reward
        for key in ["workflow_completed", "policy_adapted", "schema_adapted", "approval_correct", "api_success", "audit_complete", "sla_met"]:
            totals[key] += int(final_info.get(key, False))
        if len(samples) < 3:
            samples.append({"workflow": env.current_task["workflow"] if env.current_task else None, "reward": round(env.total_reward, 3), "final_info": final_info, "timeline": env.timeline})
    n = float(num_episodes)
    return {"agent": agent_type, "num_episodes": num_episodes, "avg_reward": round(totals["reward"] / n, 3), "workflow_success_rate": round(totals["workflow_completed"] / n, 3), "policy_adaptation_rate": round(totals["policy_adapted"] / n, 3), "schema_adaptation_rate": round(totals["schema_adapted"] / n, 3), "approval_correct_rate": round(totals["approval_correct"] / n, 3), "api_success_rate": round(totals["api_success"] / n, 3), "audit_completion_rate": round(totals["audit_complete"] / n, 3), "sla_success_rate": round(totals["sla_met"] / n, 3), "samples": samples}


def compare_agents(num_episodes: int = 25) -> Dict[str, Any]:
    return {"num_episodes": num_episodes, "results": [evaluate_agent(agent, num_episodes) for agent in AGENTS]}


if __name__ == "__main__":
    import json
    print(json.dumps(compare_agents(25), indent=2))
