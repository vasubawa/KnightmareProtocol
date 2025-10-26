import asyncio
import os
import json
from importlib import import_module
from pathlib import Path

# ---------- Environment Loader ----------
def _ensure_env_loaded() -> None:
    try:
        from dotenv import load_dotenv
    except Exception:
        load_dotenv = None

    if load_dotenv:
        load_dotenv()
        return

    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

_ensure_env_loaded()

# ---------- ADK Imports ----------
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

tool = _load_tool()
Agent = _load_agent()

# ---------- Memory Store ----------
MEMORY_FILE = Path(__file__).parent / "memory_store.json"

def _load_memory():
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ---------- ADK Tool Functions ----------
@tool()
async def store_preference(user_id: str, key: str, value: str):
    """
    Store a user preference or piece of context.
    """
    memory = _load_memory()
    if user_id not in memory:
        memory[user_id] = {}
    memory[user_id][key] = value
    _save_memory(memory)
    return f"Stored {key} for user {user_id}."

@tool()
async def get_preference(user_id: str, key: str):
    """
    Retrieve a stored user preference or context.
    """
    memory = _load_memory()
    value = memory.get(user_id, {}).get(key)
    if value is None:
        return f"No stored value for {key} for user {user_id}."
    return value

# ---------- Background Loop ----------
@tool()
async def run_ops():
    """Background operations for memory agent (currently placeholder)."""
    print("Memory agent ready...")
    return "Memory agent operational"

# ---------- Root Agent ----------
memory_agent = Agent(
    model="gemini-2.5-flash",
    name="memory_agent",
    description="Stores user preferences, history, and orchestrator context.",
    instruction="Capture relevant facts, surface context on demand, and keep data consistent.",
    tools=[store_preference, get_preference, run_ops],
)
