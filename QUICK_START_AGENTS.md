# Quick Start Guide - Agent System

## Installation

```bash
# Navigate to agent directory
cd /home/dhruvunix/with-adk/agent

# Create virtual environment (if not already created)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in `/home/dhruvunix/with-adk/agent/` with:

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional - for email functionality
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_APP_PASSWORD=your_gmail_app_password

# Optional - for commute calculations
MAPS_PLACE_API_KEY=your_google_maps_api_key

# Optional - for real flight data
AMADEUS_API_KEY=your_amadeus_key
AMADEUS_API_SECRET=your_amadeus_secret
```

### How to Get API Keys:

1. **Google AI (Gemini) API Key** (Required)
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Click "Create API Key"

2. **Gmail App Password** (Optional - for email agent)
   - Go to: https://myaccount.google.com/apppasswords
   - Sign in to your Google account
   - Select "Mail" and "Other (Custom name)"
   - Copy the 16-character password

3. **Google Maps API Key** (Optional - for commute agent)
   - Visit: https://console.cloud.google.com/
   - Create a new project or select existing
   - Enable "Distance Matrix API"
   - Create credentials → API Key

4. **Amadeus API** (Optional - for flight agent)
   - Visit: https://developers.amadeus.com/
   - Register for free developer account
   - Get API Key and Secret from dashboard

## Testing Individual Agents

### Test Development Agents:

```python
# Test Documentation Agent
python3 -c "
from root_agent.dev_agent import doc_agent
import asyncio

async def test():
    # Analyze a Python file
    result = await doc_agent.tools[0]('root_agent/agent.py')
    print(result)

asyncio.run(test())
"

# Test Linter Agent
python3 -c "
from root_agent.dev_agent import linter_agent
import asyncio

async def test():
    # Check syntax
    result = await linter_agent.tools[0]('root_agent/agent.py')
    print(result)

asyncio.run(test())
"
```

### Test Sub-Agents:

```python
# Test Memory Agent
python3 -c "
from root_agent.sub_agents.memory_agent.agent import memory_agent
import asyncio

async def test():
    # Store a preference
    result = await memory_agent.tools[0]('user123', 'favorite_color', 'blue')
    print(result)
    
    # Retrieve it
    result = await memory_agent.tools[1]('user123', 'favorite_color')
    print(result)

asyncio.run(test())
"

# Test Notification Agent
python3 -c "
from root_agent.sub_agents.notification_agent.agent import notification_agent
import asyncio

async def test():
    # Send a notification
    result = await notification_agent.tools[0](
        title='Test Notification',
        message='This is a test!',
        priority='high'
    )
    print(result)
    
    # Get notifications
    result = await notification_agent.tools[1]()
    print(result)

asyncio.run(test())
"

# Test Knowledge Agent
python3 -c "
from root_agent.sub_agents.knowledge_agent.agent import knowledge_agent
import asyncio

async def test():
    # Query Wikipedia
    result = await knowledge_agent.tools[0]('Python programming language')
    print(result)

asyncio.run(test())
"
```

## Running the Full System

### Option 1: Run Root Orchestrator

```bash
cd /home/dhruvunix/with-adk/agent/root_agent
python3 agent.py
```

This starts the FastAPI server with the personal assistant orchestrator on port 8000.

### Option 2: Run Standalone Attraction Agent

```bash
cd /home/dhruvunix/with-adk/agent
python3 agent.py
```

This starts the attraction agent FastAPI server on port 8000.

### Option 3: Import and Use Programmatically

```python
from agent.root_agent.agent import root_agent
from agent.root_agent.sub_agents.agent import root_agent as workflow_agent

# Use the agents in your code
# The agents will be configured and ready to use
```

## Verifying Everything Works

Run this comprehensive test:

```bash
cd /home/dhruvunix/with-adk

# Test all imports
python3 << 'EOF'
print("Testing agent imports...")

# Test dev agents
from agent.root_agent.dev_agent import doc_agent, linter_agent, testing_agent
print("✓ Dev agents imported successfully")

# Test sub-agents (without wikipedia dependency for now)
from agent.root_agent.sub_agents.calendar_agent.agent import calendar_agent
from agent.root_agent.sub_agents.memory_agent.agent import memory_agent
from agent.root_agent.sub_agents.notification_agent.agent import notification_agent
print("✓ Sub-agents imported successfully")

# Test root agent
from agent.root_agent.agent import root_agent
print("✓ Root agent imported successfully")

print("\n🎉 All agents loaded successfully!")
EOF
```

## Common Issues & Solutions

### Issue: `ModuleNotFoundError: No module named 'wikipedia'`
**Solution:**
```bash
pip install wikipedia
```

### Issue: `ModuleNotFoundError: No module named 'google.adk'`
**Solution:**
```bash
pip install google-adk google-genai
```

### Issue: `Missing GOOGLE_API_KEY`
**Solution:**
- Create `.env` file in `/home/dhruvunix/with-adk/agent/`
- Add: `GOOGLE_API_KEY=your_key_here`

### Issue: Email agent not working
**Solution:**
- Verify Gmail credentials in `.env`
- Enable "Less secure app access" OR use App Password
- Check firewall settings for SMTP (port 587)

### Issue: Commute agent returns error
**Solution:**
- Verify `MAPS_PLACE_API_KEY` in `.env`
- Enable Distance Matrix API in Google Cloud Console
- Check API quota limits

## Agent Capabilities Summary

| Agent | Key Functions | Dependencies |
|-------|--------------|--------------|
| **doc_agent** | Analyze code, generate docstrings, check coverage | None (stdlib only) |
| **linter_agent** | Syntax check, style linting, complexity analysis | Optional: pylint |
| **testing_agent** | Generate tests, run pytest, coverage reports | Optional: pytest, pytest-cov |
| **calendar_agent** | Schedule management | None (placeholder) |
| **commute_agent** | Travel time calculations | requests, Google Maps API |
| **critic_agent** | Plan validation | None (placeholder) |
| **email_agent** | Send emails via SMTP | smtplib (stdlib), Gmail creds |
| **flight_agent** | Flight search | Optional: amadeus |
| **focus_agent** | Focus reminders | None (placeholder) |
| **knowledge_agent** | Wikipedia queries | wikipedia |
| **memory_agent** | User preferences storage | None (JSON file) |
| **notification_agent** | Alert system | None (JSON file) |
| **planner_agent** | Itinerary creation | None (placeholder) |
| **wellness_agent** | Wellness suggestions | None (placeholder) |

## Next Steps

1. **Set up API keys** in `.env` file
2. **Install missing dependencies**: `pip install wikipedia`
3. **Test individual agents** using the examples above
4. **Run the orchestrator** to see all agents working together
5. **Check the logs** for any warnings or errors
6. **Customize agent instructions** based on your needs

For more details, see `AGENT_FIXES_SUMMARY.md`
