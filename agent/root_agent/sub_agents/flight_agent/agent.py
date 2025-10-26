import asyncio
import os
from importlib import import_module
from pathlib import Path
from datetime import datetime, timedelta
import re
import logging
from google.adk.tools import google_search

# Load .env if present
def _ensure_env_loaded() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

_ensure_env_loaded()

# Load ADK tool and Agent
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
        class _Agent:  # fallback for local dev
            def __init__(self, **kwargs):
                self.config = kwargs
        return _Agent

tool = _load_tool()
Agent = _load_agent()

# Try to import Amadeus client
try:
    from amadeus import Client
except ImportError:
    Client = None

# Build Amadeus client if keys exist
def build_amadeus_client():
    api_key = os.getenv("AMADEUS_API_KEY")
    api_secret = os.getenv("AMADEUS_API_SECRET")
    if Client and api_key and api_secret:
        try:
            return Client(client_id=api_key, client_secret=api_secret)
        except Exception as e:
            logging.warning("Amadeus client init failed: %s", e)
    return None

amadeus_client = build_amadeus_client()

# Helper to parse simple flight questions
def parse_question(question: str):
    # Simple regex for "from X to Y on DATE"
    question = question.lower()
    origin_match = re.search(r'from (\w+)', question)
    dest_match = re.search(r'to (\w+)', question)
    date_match = re.search(r'on (\d{4}-\d{2}-\d{2})', question)  # YYYY-MM-DD
    if not date_match:
        date = datetime.utcnow().date().isoformat()  # default today
    else:
        date = date_match.group(1)
    origin = origin_match.group(1).upper() if origin_match else "MCO"
    destination = dest_match.group(1).upper() if dest_match else "DXB"
    return {"origin": origin, "destination": destination, "departure_date": date, "adults": 1}

@tool()
async def run_ops(question: str):
    """
    Accepts a natural language flight request like:
    "Flight from MCO to DXB on 2025-10-25"
    """
    global amadeus_client  # <-- add this line
    flight_request = parse_question(question)
    response = None

    if amadeus_client:
        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: amadeus_client.shopping.flight_offers_search.get(
                    originLocationCode=flight_request["origin"],
                    destinationLocationCode=flight_request["destination"],
                    departureDate=flight_request["departure_date"],
                    adults=flight_request["adults"],
                )
            )
            if result.data:
                seg = result.data[0]["itineraries"][0]["segments"][0]
                response = (
                    f"Flight {seg['carrierCode']}{seg['number']} from {seg['departure']['iataCode']} "
                    f"to {seg['arrival']['iataCode']} departs at {seg['departure']['at']} and arrives at {seg['arrival']['at']}"
                )
        except Exception as exc:
            import logging
            logging.warning("Amadeus API call failed: %s", exc)
            amadeus_client = None

    if response is None:
        # Fallback dummy flight
        from datetime import datetime, timedelta
        depart = datetime.utcnow() + timedelta(hours=2)
        arrival = depart + timedelta(hours=14)
        response = (
            f"[Dummy flight] ADK123 from {flight_request['origin']} to {flight_request['destination']} "
            f"departs at {depart.isoformat()} and arrives at {arrival.isoformat()}"
        )

    return response

flight_agent = Agent(
    model="gemini-2.5-flash",
    name="flight_agent",
    description="Finds, optimizes, and books flights for upcoming travel.",
    instruction="Search for flight options, evaluate trade-offs, and confirm itineraries.",
    tools=[run_ops, google_search],
)
