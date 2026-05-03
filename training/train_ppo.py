from __future__ import annotations
import csv
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from app.env import PolicyShiftEnv
from training.state_encoder import ACTIONS, action_index_to_dict, encode_state

CHECKPOINT_DIR = Path("training/checkpoints")
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

class PolicyNet(nn.Module):
    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        self.actor = nn.Sequential(nn.Linear(state_dim, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh(), nn.Linear(64, action_dim))
        self.critic = nn.Sequential(nn.Linear(state_dim, 64), nn.Tanh(), nn.Linear(64, 1))
    def forward(self, x):
        logits = self.actor(x)
        value = self.critic(x).squeeze(-1)
        return logits, value

def train(num_episodes: int = 400, gamma: float = 0.97, lr: float = 3e-4):
    env = PolicyShiftEnv(seed=42)
    obs = env.reset()
    model = PolicyNet(len(encode_state(obs)), len(ACTIONS))
    optimizer = optim.Adam(model.parameters(), lr=lr)
    rows = []
    for ep in range(1, num_episodes + 1):
        obs = env.reset()
        log_probs, values, rewards, entropies = [], [], [], []
        done = False
        for _ in range(env.max_steps):
            state = torch.tensor(encode_state(obs), dtype=torch.float32).unsqueeze(0)
            logits, value = model(state)
            dist = torch.distributions.Categorical(logits=logits)
            action_idx = dist.sample()
            action = action_index_to_dict(int(action_idx.item()), obs)
            result = env.step(action)
            obs = result["observation"]
            log_probs.append(dist.log_prob(action_idx).squeeze(0))
            values.append(value.squeeze(0))
            rewards.append(float(result["reward"]))
            entropies.append(dist.entropy().squeeze(0))
            done = result["done"]
            if done:
                break
        if not done:
            result = env.step({"action_type": "finish", "payload": {}})
            rewards.append(float(result["reward"]))
        returns, G = [], 0.0
        for r in reversed(rewards):
            G = r + gamma * G
            returns.insert(0, G)
        returns_t = torch.tensor(returns[: len(values)], dtype=torch.float32)
        values_t = torch.stack(values)
        log_probs_t = torch.stack(log_probs)
        entropies_t = torch.stack(entropies)
        advantages = returns_t - values_t.detach()
        loss = -(log_probs_t * advantages).mean() + 0.5 * nn.functional.mse_loss(values_t, returns_t) - 0.01 * entropies_t.mean()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        rows.append({"episode": ep, "reward": round(env.total_reward, 3), "loss": round(float(loss.item()), 5)})
        if ep % 25 == 0 or ep == 1:
            avg_last = np.mean([r["reward"] for r in rows[-25:]])
            print(f"Episode {ep}/{num_episodes} | reward={env.total_reward:.2f} | avg_last_25={avg_last:.2f}")
    torch.save(model.state_dict(), CHECKPOINT_DIR / "policyshift_ppo.pt")
    with open(CHECKPOINT_DIR / "episode_rewards.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["episode", "reward", "loss"])
        writer.writeheader(); writer.writerows(rows)
    print("Saved model:", CHECKPOINT_DIR / "policyshift_ppo.pt")
    print("Saved rewards:", CHECKPOINT_DIR / "episode_rewards.csv")

if __name__ == "__main__":
    train()
