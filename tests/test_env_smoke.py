from app.env import PolicyShiftEnv
from agents.rule_based import rule_based_agent

def test_rule_agent_finishes_positive():
    env = PolicyShiftEnv(); obs = env.reset(); done = False
    while not done:
        action = rule_based_agent(obs)
        result = env.step(action)
        obs = result["observation"]; done = result["done"]
    assert env.total_reward > 0
