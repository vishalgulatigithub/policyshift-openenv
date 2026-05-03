---
title: PolicyShift OpenEnv
emoji: 🔁
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---


# PolicyShift OpenEnv

### Training agents to survive policy drift, API drift, compliance drift, approval drift, SLA pressure, and audit-trail requirements.

Most agent benchmarks assume the world is static. Real enterprises are not static.

Policies change. APIs change. Approval thresholds change. Compliance rules change. SLA clocks keep running. Audit logs are mandatory. A workflow that was correct yesterday can become unsafe today.

**PolicyShift OpenEnv** is an OpenEnv-style environment for long-horizon enterprise workflow adaptation.

The agent must complete realistic enterprise workflows while detecting and adapting to:

- **Policy drift**: old policy says one thing, current policy says another.
- **API drift**: old payload fields are deprecated and rejected.
- **Compliance drift**: privacy/audit requirements change.
- **Approval drift**: thresholds and approver chains change.
- **SLA pressure**: delayed actions create penalties.
- **Audit trail requirements**: safe workflows must be explainable and logged.

---

## Why this is unique

This is not a generic API-drift environment. The challenge is the combination of:

```text
policy drift + API drift + compliance drift + approval drift + SLA pressure + audit trail
```

The agent must update its belief about the current enterprise world and complete the workflow safely.

---

## Folder structure

```text
policyshift-openenv/
├── app/
│   ├── env.py
│   ├── main.py
│   ├── models.py
│   ├── reward.py
│   ├── tasks.py
│   └── tools.py
├── agents/
│   ├── random_agent.py
│   ├── stale_policy_agent.py
│   └── rule_based.py
├── training/
│   ├── state_encoder.py
│   ├── train_ppo.py
│   └── evaluate.py
├── visualization/
│   ├── dashboard.py
│   ├── plot_rewards.py
│   └── compare_agents.py
├── baseline/
│   └── run_baseline.py
├── demo/
│   └── run_demo.py
├── data/
├── Dockerfile
├── openenv.yaml
├── requirements.txt
└── README.md
```

---

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Run baseline comparison:

```bash
python -m baseline.run_baseline
```

Train PPO:

```bash
python -m training.train_ppo
```

Evaluate agents:

```bash
python -m training.evaluate
```

Generate plots:

```bash
python visualization/plot_rewards.py
python -m visualization.compare_agents
```

Run dashboard:

```bash
streamlit run visualization/dashboard.py
```

Run API:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

## Docker

```bash
docker build -t policyshift-openenv .
docker run --rm -p 7860:7860 policyshift-openenv
```

Open:

```text
http://localhost:7860
http://localhost:7860/api/docs
```

---

## API examples

```bash
curl -X POST "http://127.0.0.1:8000/reset"

curl -X POST "http://127.0.0.1:8000/step" \
  -H "Content-Type: application/json" \
  -d '{"action_type":"read_policy","payload":{"version":"current"}}'

curl -X GET "http://127.0.0.1:8000/compare_agents?num_episodes=20"
```

---

## Winning story

> Most agents fail because they assume yesterday’s rules still apply. PolicyShift OpenEnv trains agents to detect when enterprise reality has changed, adapt their workflow, and complete business tasks safely under compliance and SLA pressure.
