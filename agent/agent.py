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
async def run_ops():
    print("Starting attraction_agent agent...")
    while True:
        print("attraction_agent agent running main loop...")
        await asyncio.sleep(3)


# ============================================================================
# Import the Root Agent with all sub-agents
# ============================================================================
try:
    from root_agent.agent import root_agent as personal_assistant
except ImportError:
    # Fallback if import fails
    personal_assistant = Agent(
        model="gemini-2.5-flash",
        name="personal_assistant",
        description="Comprehensive personal assistant with email, knowledge, calendar, and more.",
        instruction="You are a helpful personal assistant. Help users with various tasks.",
        tools=[run_ops],
    )

# Keep attraction_agent for backward compatibility, but use personal_assistant by default
root_agent = personal_assistant

# ============================================================================
# FastAPI Frontend Integration Layer
# ============================================================================
# The code below enables this agent to work with the frontend while preserving
# the original agent definition above.

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
    from google.adk.agents import LlmAgent
    
    # Use the imported root_agent (personal_assistant) with all sub-agents
    frontend_agent = root_agent
    
    # Create ADK middleware agent instance
    adk_agent = ADKAgent(
        adk_agent=frontend_agent,
        app_name="personal_assistant",
        user_id="demo_user",
        session_timeout_seconds=3600,
        use_in_memory_services=True
    )
    
    # Create FastAPI app
    app = FastAPI(title="Personal Assistant Agent with All Sub-Agents")
    
    # Add CORS middleware to allow requests from your Vercel frontend
    # Configure allowed origins based on environment
    allowed_origins = [
        "http://localhost:3000",  # Local development
        "http://127.0.0.1:3000",  # Local development alternative
        "https://aiagentic.onrender.com",  # Render deployment
    ]
    
    # Add your Vercel domain when deployed
    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        allowed_origins.append(f"https://{vercel_url}")
    
    # Add custom frontend URL if specified
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        allowed_origins.append(frontend_url)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins if os.getenv("ENVIRONMENT") == "production" else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add the ADK endpoint
    add_adk_fastapi_endpoint(app, adk_agent, path="/")
    
except ImportError:
    # FastAPI dependencies not available, agent can still work standalone
    app = None
    print("Note: FastAPI integration not available. Install fastapi, uvicorn, and ag-ui-adk for frontend support.")


if __name__ == "__main__":
    if app is not None:
        import uvicorn
        
        # Check if GOOGLE_API_KEY is set in the environment
        if not os.getenv("GOOGLE_API_KEY"):
            print("⚠️  Warning: GOOGLE_API_KEY environment variable not set!")
            print("   Set it in your .env file as GOOGLE_API_KEY=your-key-here")
            print("   Get a key from: https://makersuite.google.com/app/apikey")
            print()
        
        port = int(os.getenv("PORT", 8000))
        print(f"Starting FastAPI server on http://0.0.0.0:{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("Running original agent (no FastAPI)...")
        # You can add original agent logic here if needed
