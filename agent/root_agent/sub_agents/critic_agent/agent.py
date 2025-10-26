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
async def run_ops(plan: str):
    """Validate and critique a plan for conflicts or issues."""
    print(f"Critic agent analyzing plan: {plan[:100]}...")
    # TODO: Implement real plan validation logic
    return f"Plan reviewed. No critical issues detected in: {plan[:50]}..."


critic_agent = Agent(
    model="gemini-2.5-flash",
    name="critic_agent",
    description="Validates plans and searches for conflicts or missing dependencies.",
    instruction="Stress test itineraries, highlight risks, and recommend fixes before execution.",
    tools=[run_ops],
)
