from __future__ import annotations
from agents.rule_based import rule_based_agent
from app.env import PolicyShiftEnv

env = PolicyShiftEnv(); obs = env.reset()
print("=== PolicyShift OpenEnv Demo ===")
print("Task:", obs["visible"]["user_request"])
print("Workflow:", obs["visible"]["workflow"])
done = False
while not done:
    action = rule_based_agent(obs)
    result = env.step(action)
    obs = result["observation"]; done = result["done"]
    print("\nAction:", action)
    print("Reward:", result["reward"])
    print("Message:", result["info"]["event"]["message"])
print("\nTotal reward:", round(env.total_reward, 3))
