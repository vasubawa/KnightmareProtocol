import asyncio
import os
from importlib import import_module
from pathlib import Path


def _ensure_env_loaded() -> None:
    try:
        from dotenv import load_dotenv
    except Exception:  # pragma: no cover - optional dependency
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


def _load_tool():
    try:
        return getattr(import_module("google.adk.framework.tool"), "tool")
    except Exception:  # pragma: no cover - fallback for local dev
        def noop_decorator():
            def decorator(func):
                return func

            return decorator

        return noop_decorator


def _load_agent():
    try:
        return getattr(import_module("google.adk.agents.llm_agent"), "Agent")
    except Exception:  # pragma: no cover - fallback shim for local dev
        class _Agent:  # type: ignore
            def __init__(self, **kwargs):
                self.config = kwargs

        return _Agent


tool = _load_tool()
Agent = _load_agent()


@tool()
async def run_ops(activity_type: str = "general"):
    """Suggest wellness activities and self-care recommendations."""
    suggestions = {
        "general": "Take a 5-minute break, stretch, and hydrate.",
        "break": "Step away from your screen, do some light stretching, and take deep breaths.",
        "exercise": "Consider a 10-minute walk or quick workout session.",
        "mindfulness": "Try a 2-minute breathing exercise or brief meditation."
    }
    suggestion = suggestions.get(activity_type, suggestions["general"])
    print(f"Wellness agent suggests: {suggestion}")
    return f"Wellness recommendation: {suggestion}"


wellness_agent = Agent(
    model="gemini-2.5-flash",
    name="wellness_agent",
    description="Suggests breaks and self-care activities to maintain balance.",
    instruction="Monitor workload, recommend restorative breaks, and encourage healthy habits.",
    tools=[run_ops],
)
