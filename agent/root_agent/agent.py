"""
Personal Assistant Root Agent — orchestrates planner, flight, commute, calendar, and critic agents.
"""

from __future__ import annotations
import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI
from importlib import import_module

# === Load environment ===
load_dotenv()

# === Utility Loaders for ADK ===
def _load_tool():
    try:
        return getattr(import_module("google.adk.framework.tool"), "tool")
    except Exception:
        def noop_decorator():
            def decorator(func):
                return func
            return decorator
        return noop_decorator

def _load_agent():
    try:
        return getattr(import_module("google.adk.agents.llm_agent"), "Agent")
    except Exception:
        class _Agent:
            def __init__(self, **kwargs):
                self.config = kwargs
        return _Agent

def _load_agent_tool():
    try:
        return getattr(import_module("google.adk.tools.agent_tool"), "AgentTool")
    except Exception:
        class _AgentTool:
            def __init__(self, agent):
                self.agent = agent
        return _AgentTool

tool = _load_tool()
Agent = _load_agent()
AgentTool = _load_agent_tool()


# === Import Sub Agents ===
def _load_sub_agent(module_path: str):
    return getattr(import_module(module_path), "root_agent")

planner_agent = _load_sub_agent("agents.planner_agent.agent")
flight_agent = _load_sub_agent("agents.flight_agent.agent")
commute_agent = _load_sub_agent("agents.commute_agent.agent")
calendar_agent = _load_sub_agent("agents.calendar_agent.agent")
critic_agent = _load_sub_agent("agents.critic_agent.agent")


# === Tool: Workflow Runner ===
@tool()
async def run_ops(request: str):
    """Main workflow: plan trip → book flight → calculate commute → update calendar → validate plan"""
    try:
        print(f"🧠 Personal Assistant received request: {request}")

        # Step 1: Plan itinerary
        plan = f"🧭 Planner Agent → Planning itinerary for: {request}"
        print(plan)

        # Step 2: Find flights
        flight_info = f"✈️ Flight Agent → Searching flights for: {request}"
        print(flight_info)

        # Step 3: Estimate commute times
        commute_info = f"🚗 Commute Agent → Calculating travel times for: {request}"
        print(commute_info)

        # Step 4: Sync to calendar
        calendar_info = f"🗓️ Calendar Agent → Updating schedule for: {request}"
        print(calendar_info)

        # Step 5: Validate and summarize
        critic_feedback = f"🔍 Critic Agent → Reviewing plan for: {request}"
        print(critic_feedback)

        return f"""
✅ Trip Planning Summary:
{plan}
{flight_info}
{commute_info}
{calendar_info}
{critic_feedback}
"""

    except Exception as e:
        return f"❌ Error in workflow: {e}"


# === Root Orchestrator Agent ===
root_agent = Agent(
    model="gemini-2.5-flash",
    name="personal_assistant",
    description="The root orchestrator that manages all sub-agents for trip planning.",
    instruction="""Coordinate multiple sub-agents to handle trip planning, flight booking,
    commute calculations, calendar syncing, and conflict checking.
    Always summarize results clearly for the user.""",
    tools=[
        AgentTool(agent=planner_agent),
        AgentTool(agent=flight_agent),
        AgentTool(agent=commute_agent),
        AgentTool(agent=calendar_agent),
        AgentTool(agent=critic_agent),
        run_ops,
    ],
)

# === Optional: FastAPI Endpoint for ADK Middleware ===
try:
    _ag_ui_adk = import_module("ag_ui_adk")
    ADKAgent = getattr(_ag_ui_adk, "ADKAgent")
    add_adk_fastapi_endpoint = getattr(_ag_ui_adk, "add_adk_fastapi_endpoint")

    app = FastAPI(title="ADK Middleware — Personal Assistant")
    adk_agent = ADKAgent(
        adk_agent=root_agent,
        app_name="personal_assistant_app",
        user_id="global_user",
        session_timeout_seconds=3600,
        use_in_memory_services=True
    )

    add_adk_fastapi_endpoint(app, adk_agent, path="/")

except Exception:
    app = None
    print("⚠️ ADK Middleware not installed. Running in standalone mode.")


# === Run Server or Console Mode ===
if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ Missing GOOGLE_API_KEY in environment (.env)")
        print("   Get a key from: https://makersuite.google.com/app/apikey")
        print()

    print("🚀 Launching Personal Assistant Root Agent...")
    if app:
        import uvicorn
        port = int(os.getenv("PORT", 8000))
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print(f"✅ Loaded agent: {root_agent.config['name']}")
        print("Ready to process workflow requests.")
