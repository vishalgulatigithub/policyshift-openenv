from __future__ import annotations
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from app.env import PolicyShiftEnv
from app.models import ActionRequest
from app.tasks import load_tasks
from training.evaluate import compare_agents, evaluate_agent

app = FastAPI(title="PolicyShift OpenEnv API", description="OpenEnv-style environment for policy drift, API drift, compliance drift, approval drift, SLA pressure, and audit trails.", version="0.1.0")
env = PolicyShiftEnv()

@app.get("/")
def root():
    return {"name": "PolicyShift OpenEnv", "status": "running", "docs": "/docs", "problem": "Agents must complete enterprise workflows while adapting to policy/API/compliance drift."}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset():
    return env.reset()

@app.post("/step")
def step(action: ActionRequest):
    return env.step(action)

@app.get("/state")
def state():
    return env.get_state()

@app.get("/tasks")
def tasks(limit: int = Query(10, ge=1, le=100)):
    return {"tasks": load_tasks(n=limit)}

@app.get("/evaluate_agent")
def api_evaluate_agent(agent_type: str = Query(..., description="random | stale_policy | rule"), num_episodes: int = Query(25, ge=1, le=200)):
    return JSONResponse(content=evaluate_agent(agent_type, num_episodes))

@app.get("/compare_agents")
def api_compare_agents(num_episodes: int = Query(25, ge=1, le=200)):
    return JSONResponse(content=compare_agents(num_episodes))
