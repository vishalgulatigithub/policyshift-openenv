from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from training.evaluate import compare_agents
result = compare_agents(40)
rows = [{k: v for k, v in r.items() if k != "samples"} for r in result["results"]]
df = pd.DataFrame(rows)
print(df)
metrics = ["avg_reward", "workflow_success_rate", "policy_adaptation_rate", "schema_adaptation_rate", "approval_correct_rate", "api_success_rate", "audit_completion_rate", "sla_success_rate"]
for metric in metrics:
    plt.figure(figsize=(8, 4))
    plt.bar(df["agent"], df[metric])
    plt.title(metric.replace("_", " ").title())
    plt.xlabel("Agent"); plt.ylabel(metric); plt.grid(axis="y", alpha=0.3)
    out = Path(f"visualization/{metric}_comparison.png")
    plt.savefig(out, bbox_inches="tight")
    print("Saved", out)
