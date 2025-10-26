import asyncio
import os
from importlib import import_module
from pathlib import Path
import wikipedia


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


@tool()
async def run_ops(question: str):
    """Fetch a short Wikipedia summary for the given question."""
    try:
        wikipedia.set_lang("en")
        summary = wikipedia.summary(question, sentences=3)
        return summary
    except wikipedia.DisambiguationError as e:
        return f"Your query is ambiguous, did you mean one of: {e.options[:5]}"
    except wikipedia.PageError:
        return "No page found for your query."
    except Exception as e:
        return f"An error occurred: {e}"


knowledge_agent = Agent(
    model="gemini-2.5-flash",
    name="knowledge_agent",
    description="Provides research, reference, and knowledge support on demand.",
    instruction="Answer questions with sourced insights and help users learn quickly.",
    tools=[run_ops],
)
