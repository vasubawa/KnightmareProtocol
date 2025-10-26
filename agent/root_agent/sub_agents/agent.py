# Assuming this is your main agent.py file at the root level

from google.adk.agents import ParallelAgent, SequentialAgent

# --- Import ALL necessary subagents from your existing folders ---
from sub_agents.calendar_agent import calendar_agent
from sub_agents.flight_agent import flight_agent
from sub_agents.commute_agent import commute_agent
from sub_agents.planner_agent import planner_agent
from sub_agents.notification_agent import notification_agent
from sub_agents.critic_agent import critic_agent         # Added
from sub_agents.email_agent import email_agent           # Added
from sub_agents.focus_agent import focus_agent           # Added
from sub_agents.knowledge_agent import knowledge_agent   # Added
from sub_agents.memory_agent import memory_agent         # Added
from sub_agents.test_agent import test_agent             # Added (Assuming this exists)
from sub_agents.wellness_agent import wellness_agent     # Added

# --- 1. Define the Parallel Agent Step ---
# This runs the planning agents concurrently
personal_assistant_planners = ParallelAgent(
    name="personal_assistant_parallel_planner",
    sub_agents=[
        planner_agent,
        calendar_agent,
        flight_agent,
        commute_agent
        ],
    description="Gathers trip planning information (itinerary, schedule, flights, commute) in parallel."
)

# --- 2. Define the Sequential Pipeline (This IS the Root Agent) ---
# Step 1: Run the planners in parallel
# Step 2: Run the notification agent
# Step 3 onwards: Run the rest of the agents sequentially
root_agent = SequentialAgent(
    name="full_personal_assistant_workflow", # Updated name for clarity
    sub_agents=[
        personal_assistant_planners, # Step 1: Gather info concurrently
        notification_agent,        # Step 2: Send initial notification
        critic_agent,              # Step 3: Critique the plan?
        email_agent,               # Step 4: Email the plan?
        focus_agent,               # Step 5: Set focus reminders?
        knowledge_agent,           # Step 6: Consult knowledge base?
        memory_agent,              # Step 7: Save to memory?
        # test_agent,              # Step 8: (Include if you have a specific test step)
        wellness_agent             # Step 9: Add wellness suggestions?
    ],
    description="Orchestrates the full Personal Assistant workflow: plans in parallel, notifies, then processes sequentially through critique, email, focus, knowledge, memory, and wellness steps."
)

# --- IMPORTANT ---
# Each agent in the sequence needs appropriate instructions.
# - notification_agent: Needs instructions on what to notify about initially.
# - critic_agent: Needs instructions on what to critique (e.g., the plan generated).
# - email_agent: Needs instructions on what to email and to whom.
# - focus_agent: Needs instructions on what reminders to set based on the plan.
# - knowledge_agent: Needs instructions on what information to look up or cross-reference.
# - memory_agent: Needs instructions on what details of the plan to save.
# - wellness_agent: Needs instructions on how to add wellness tips related to the plan.
#
# Remember that each agent in the sequence will receive the state,
# including outputs from all previous steps. Update their individual
# 'instruction' parameters accordingly.