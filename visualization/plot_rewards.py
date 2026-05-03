from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
path = Path("training/checkpoints/episode_rewards.csv")
if not path.exists():
    raise FileNotFoundError("Run python -m training.train_ppo first.")
df = pd.read_csv(path)
df["moving_avg_25"] = df["reward"].rolling(25).mean()
plt.figure(figsize=(12, 5))
plt.plot(df["episode"], df["reward"], alpha=0.4, label="Episode Reward")
plt.plot(df["episode"], df["moving_avg_25"], label="Moving Average (25)")
plt.xlabel("Episode"); plt.ylabel("Reward"); plt.title("PolicyShift PPO Training Reward Curve")
plt.legend(); plt.grid(True)
out = Path("visualization/reward_curve.png")
plt.savefig(out, bbox_inches="tight")
print("Saved", out)
