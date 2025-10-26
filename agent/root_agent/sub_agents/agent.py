"""
Multi-Agent Orchestrator using Parallel and Sequential Agents
This orchestrator coordinates all sub-agents in the personal assistant system.
"""

from importlib import import_module

# === Load ADK Agent Classes ===
def _load_parallel_agent():
    try:
        return getattr(import_module("google.adk.agents"), "ParallelAgent")
    except Exception:
        class _ParallelAgent:
            def __init__(self, **kwargs):
                self.config = kwargs
        return _ParallelAgent

def _load_sequential_agent():
    try:
        return getattr(import_module("google.adk.agents"), "SequentialAgent")
    except Exception:
        class _SequentialAgent:
            def __init__(self, **kwargs):
                self.config = kwargs
        return _SequentialAgent

ParallelAgent = _load_parallel_agent()
SequentialAgent = _load_sequential_agent()

# === Import Sub-Agents ===
def _load_agent(module_path: str, agent_name: str):
    """Safely load an agent from a module."""
    try:
        module = import_module(module_path)
        return getattr(module, agent_name)
    except Exception as e:
        print(f"Warning: Could not load {agent_name} from {module_path}: {e}")
        return None

# Load all sub-agents
calendar_agent = _load_agent(".calendar_agent.agent", "calendar_agent")
flight_agent = _load_agent(".flight_agent.agent", "flight_agent")
commute_agent = _load_agent(".commute_agent.agent", "commute_agent")
planner_agent = _load_agent(".planner_agent.agent", "planner_agent")
notification_agent = _load_agent(".notification_agent.agent", "notification_agent")
critic_agent = _load_agent(".critic_agent.agent", "critic_agent")
email_agent = _load_agent(".email_agent.agent", "email_agent")
focus_agent = _load_agent(".focus_agent.agent", "focus_agent")
knowledge_agent = _load_agent(".knowledge_agent.agent", "knowledge_agent")
memory_agent = _load_agent(".memory_agent.agent", "memory_agent")
wellness_agent = _load_agent(".wellness_agent.agent", "wellness_agent")

# Filter out None values (agents that failed to load)
available_agents = {
    "planner": planner_agent,
    "calendar": calendar_agent,
    "flight": flight_agent,
    "commute": commute_agent,
    "notification": notification_agent,
    "critic": critic_agent,
    "email": email_agent,
    "focus": focus_agent,
    "knowledge": knowledge_agent,
    "memory": memory_agent,
    "wellness": wellness_agent,
}

# Remove None entries
available_agents = {k: v for k, v in available_agents.items() if v is not None}

# === 1. Define the Parallel Agent Step ===
# This runs the planning agents concurrently
parallel_planners = []
for name in ["planner", "calendar", "flight", "commute"]:
    if name in available_agents:
        parallel_planners.append(available_agents[name])

if parallel_planners:
    personal_assistant_planners = ParallelAgent(
        name="personal_assistant_parallel_planner",
        sub_agents=parallel_planners,
        description="Gathers trip planning information (itinerary, schedule, flights, commute) in parallel."
    )
else:
    personal_assistant_planners = None

# === 2. Define the Sequential Pipeline ===
# Build sequential agent list
sequential_agents = []
if personal_assistant_planners:
    sequential_agents.append(personal_assistant_planners)

# Add remaining agents in order
for name in ["notification", "critic", "email", "focus", "knowledge", "memory", "wellness"]:
    if name in available_agents:
        sequential_agents.append(available_agents[name])

# Create the root orchestrator agent
if sequential_agents:
    root_agent = SequentialAgent(
        name="full_personal_assistant_workflow",
        sub_agents=sequential_agents,
        description="Orchestrates the full Personal Assistant workflow: plans in parallel, notifies, then processes sequentially through critique, email, focus, knowledge, memory, and wellness steps."
    )
else:
    # Fallback if no agents loaded
    print("Warning: No agents loaded for orchestrator!")
    root_agent = None