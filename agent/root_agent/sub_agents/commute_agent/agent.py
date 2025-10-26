import asyncio
import os
import requests
from importlib import import_module
from pathlib import Path

# Load environment variables
def _ensure_env_loaded() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
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

# Google Maps Distance Tool
@tool()
async def run_ops(origin: str, destination: str) -> str:
    """Return driving distance and duration between origin and destination using Google Maps."""
    api_key = os.getenv("MAPS_PLACE_API_KEY")
    if not api_key:
        return "Error: MAPS_PLACE_API_KEY not set in environment variables."

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": destination,
        "key": api_key,
        "units": "imperial",
    }

    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        if data.get("status") != "OK":
            return f"Error from Google Maps API: {data.get('status')}"

        element = data["rows"][0]["elements"][0]
        if element.get("status") != "OK":
            return f"Cannot calculate distance: {element.get('status')}"

        distance = element["distance"]["text"]
        duration = element["duration"]["text"]
        return f"The distance from {origin} to {destination} is {distance}, and it will take approximately {duration} by car."
    except Exception as e:
        return f"An error occurred: {e}"

# Root agent configuration
commute_agent = Agent(
    model="gemini-2.5-flash",
    name="commute_agent",
    description="Calculates door-to-door travel durations and best routes.",
    instruction="Estimate travel times, highlight delays, and suggest optimal departure windows.",
    tools=[run_ops],
)
