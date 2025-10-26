# Knight Hacks OPS Agents

A Google ADK multi-agent workspace that demonstrates how a coordinated set of productivity agents (travel, scheduling, focus, etc.) can serve a program manager. Every agent exposes a `root_agent` entry point for the ADK CLI/UI and falls back gracefully when optional third-party SDKs are missing.

## Repository Layout

```
├── my_agent/              # Simple Q&A assistant (starter template)
├── planner_agent/         # Builds itineraries and reconciles schedules
├── calendar_agent/        # Tracks calendar events and detects conflicts
├── flight_agent/          # Calls Amadeus for live fares with dummy fallback
├── commute_agent/         # Uses Google Maps Distance Matrix when available
├── notification_agent/    # Surfaces alerts and reminders
├── email_agent/           # Drafts status updates and responses
├── focus_agent/           # Manages deep-work blocks and nudges
├── critic_agent/          # QA gatekeeper that reviews other agents
├── memory_agent/          # Consolidates long-term memory signals
├── attraction_agent/      # Suggests local activities for upcoming trips
├── wellness_agent/        # Recommends rest and wellness actions
├── knowledge_agent/       # Answers background questions from context
├── notification_agent/    # Notification routing (event-driven)
├── main.py                # Legacy orchestrator demo (optional)
└── README.md
```

Each agent exports `root_agent` so that `adk web <agent_folder>` works out of the box. The shared `.env` at the repo root stores API keys consumed by every agent.

## Prerequisites

- Python 3.10 or newer
- Google ADK CLI (`pip install google-adk`)
- Optional SDKs per agent:
  - `python-dotenv` for automatic `.env` loading (otherwise we parse manually)
  - `googlemaps` for `commute_agent`
  - `amadeus` for `flight_agent`

Install missing packages inside your virtualenv, for example:

```bash
pip install python-dotenv googlemaps amadeus
```

## Environment Configuration

Create `.env` at the repository root (already checked in for convenience) and populate the keys you have access to:

```
GOOGLE_API_KEY=...          # Required for Gemini 2.5 Flash
MAPS_PLACE_API_KEY=...      # Needed for live commute estimates (optional)
AMADEUS_API_KEY=...
AMADEUS_API_SECRET=...
```

All agent modules call `_ensure_env_loaded()` during import, so running the ADK CLI/W UI inherits these variables automatically. If you prefer exporting variables manually, `source .env` before launching the agents.

## Running An Agent In The ADK Web UI

```bash
cd /Users/<you>/Dev/knight-hacks-25
source .venv/bin/activate        # optional but recommended
source .env                       # if you want to push vars into your shell
adk web planner_agent             # replace with any other agent folder name
```

Repeat the last command with `calendar_agent`, `flight_agent`, etc. The ADK UI will display the agent description, and every prompt you send is routed through that agent’s `run_ops` tool. For example:

- `commute_agent`: ask “from New York to Boston” to trigger a Distance Matrix call or fallback guidance.
- `flight_agent`: ask “Flight from MCO to DXB on 2025-12-01” to try the Amadeus API.

If the required SDK or API key is missing, the agent returns an informative fallback message instead of failing.

## Orchestrator Demo (Optional)

`main.py` shows the earlier orchestrated productivity simulation that wires multiple domain agents together. It depends on an `ops` package that lives outside this repository snapshot, so treat it as illustrative unless you restore those modules.

## Troubleshooting

- **Import "amadeus" could not be resolved**: install `amadeus` inside the same virtualenv you use for the ADK CLI.
- **Google Maps quota or auth errors**: confirm `MAPS_PLACE_API_KEY` (or `GOOGLE_MAPS_API_KEY`) is present in `.env` and valid for Distance Matrix.
- **Agent not shown in ADK web**: ensure the folder’s `__init__.py` re-exports `root_agent` (already configured) and that you invoke `adk web <folder>` from the repo root.

## Next Steps

- Add additional tools to each agent, e.g., calendar CRUD, email send, or focus analytics.
- Wire the agents back into a shared orchestrator once their standalone behaviors are proven.
- Capture integration secrets with a proper secrets manager instead of a plain `.env` file when moving toward production.
