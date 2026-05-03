from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import pandas as pd
import streamlit as st
from agents.rule_based import rule_based_agent
from app.env import PolicyShiftEnv
from training.evaluate import compare_agents, evaluate_agent

st.set_page_config(page_title="PolicyShift OpenEnv", layout="wide")
st.title("PolicyShift OpenEnv")
st.caption("Policy drift + API drift + compliance drift + approval drift + SLA pressure + audit trail")
st.markdown("""
### Real-world problem
Most agents assume yesterday's rules still apply. In enterprises, policies, APIs, approvals, and compliance rules change constantly.

This environment tests whether an agent can inspect the current world, avoid stale assumptions, and complete workflows safely.
""")
with st.sidebar:
    episodes = st.slider("Episodes per agent", 5, 100, 25)
tab1, tab2, tab3 = st.tabs(["Agent Comparison", "Workflow Replay", "Single Agent JSON"])
with tab1:
    if st.button("Run Comparison"):
        result = compare_agents(episodes)
        rows = [{k: v for k, v in r.items() if k != "samples"} for r in result["results"]]
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("agent")[["avg_reward"]])
        st.bar_chart(df.set_index("agent")[["workflow_success_rate", "policy_adaptation_rate", "schema_adaptation_rate", "sla_success_rate"]])
with tab2:
    st.markdown("### Rule-based successful replay")
    env = PolicyShiftEnv(); obs = env.reset()
    st.write("**Task:**", obs["visible"]["user_request"])
    done = False; replay = []
    while not done:
        action = rule_based_agent(obs)
        result = env.step(action)
        obs = result["observation"]; done = result["done"]
        replay.append(result["info"]["event"])
    st.dataframe(pd.DataFrame(replay), use_container_width=True)
    st.metric("Total Reward", round(env.total_reward, 3))
with tab3:
    agent = st.selectbox("Agent", ["random", "stale_policy", "rule"])
    n = st.slider("Eval episodes", 1, 50, 10)
    if st.button("Evaluate"):
        st.json(evaluate_agent(agent, n))
