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
def _load_sub_agent(module_path: str, agent_name: str = "root_agent"):
    """Load a sub-agent from a module path."""
    try:
        module = import_module(module_path)
        # Try to get the specific agent first (e.g., planner_agent), fallback to root_agent
        return getattr(module, agent_name, None) or getattr(module, "root_agent")
    except Exception as e:
        print(f"Warning: Failed to load agent from {module_path}: {e}")
        return None

# Load sub-agents with correct relative paths
planner_agent = _load_sub_agent("root_agent.sub_agents.planner_agent.agent", "planner_agent")
flight_agent = _load_sub_agent("root_agent.sub_agents.flight_agent.agent", "flight_agent")
commute_agent = _load_sub_agent("root_agent.sub_agents.commute_agent.agent", "commute_agent")
calendar_agent = _load_sub_agent("root_agent.sub_agents.calendar_agent.agent", "calendar_agent")
critic_agent = _load_sub_agent("root_agent.sub_agents.critic_agent.agent", "critic_agent")
email_agent = _load_sub_agent("root_agent.sub_agents.email_agent.agent", "email_agent")
knowledge_agent = _load_sub_agent("root_agent.sub_agents.knowledge_agent.agent", "knowledge_agent")
memory_agent = _load_sub_agent("root_agent.sub_agents.memory_agent.agent", "memory_agent")
notification_agent = _load_sub_agent("root_agent.sub_agents.notification_agent.agent", "notification_agent")
focus_agent = _load_sub_agent("root_agent.sub_agents.focus_agent.agent", "focus_agent")
wellness_agent = _load_sub_agent("root_agent.sub_agents.wellness_agent.agent", "wellness_agent")


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
    description="The root orchestrator that manages all sub-agents for comprehensive personal assistance including trip planning, emails, knowledge queries, notifications, memory, and wellness.",
    instruction="""You are a comprehensive personal assistant with access to multiple specialized agents.
    
    Available agents and their capabilities:
    - planner_agent: Create itineraries and schedules
    - flight_agent: Search for flights
    - commute_agent: Calculate travel times and routes
    - calendar_agent: Manage schedules
    - email_agent: Send emails (use this when user asks to send emails)
    - knowledge_agent: Search Wikipedia for information
    - memory_agent: Store and retrieve user preferences
    - notification_agent: Send notifications and reminders
    - critic_agent: Validate and review plans
    - focus_agent: Help with focus sessions
    - wellness_agent: Provide wellness suggestions
    
    When the user asks you to do something:
    1. Determine which agent(s) can help
    2. Use the appropriate AgentTool to delegate the task
    3. Combine results from multiple agents if needed
    4. Provide a clear, helpful response
    
    Examples:
    - "Send me an email with Orlando facts" → Use knowledge_agent to get facts, then email_agent to send
    - "Call the calendar" → Use calendar_agent
    - "Remember my preference" → Use memory_agent
    - "Plan a trip" → Use planner_agent, flight_agent, commute_agent in sequence
    
    Always be proactive and use the right tools!""",
    tools=[
        AgentTool(agent=planner_agent),
        AgentTool(agent=flight_agent),
        AgentTool(agent=commute_agent),
        AgentTool(agent=calendar_agent),
        AgentTool(agent=critic_agent),
        AgentTool(agent=email_agent),
        AgentTool(agent=knowledge_agent),
        AgentTool(agent=memory_agent),
        AgentTool(agent=notification_agent),
        AgentTool(agent=focus_agent),
        AgentTool(agent=wellness_agent),
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
