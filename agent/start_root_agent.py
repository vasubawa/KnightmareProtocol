#!/usr/bin/env python3
"""
Start the Personal Assistant Root Agent Server
This agent can access all sub-agents including email, knowledge, calendar, etc.
"""

import os
from pathlib import Path

# Ensure we're in the right directory
os.chdir(Path(__file__).parent)

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" 🤖 PERSONAL ASSISTANT ROOT AGENT SERVER")
    print("="*60)
    print("\nStarting server with all sub-agents enabled:")
    print("  ✓ planner_agent")
    print("  ✓ flight_agent")
    print("  ✓ commute_agent")
    print("  ✓ calendar_agent")
    print("  ✓ email_agent (can send emails)")
    print("  ✓ knowledge_agent (Wikipedia queries)")
    print("  ✓ memory_agent (user preferences)")
    print("  ✓ notification_agent (alerts & reminders)")
    print("  ✓ critic_agent (plan validation)")
    print("  ✓ focus_agent (focus sessions)")
    print("  ✓ wellness_agent (wellness tips)")
    print("\n" + "="*60 + "\n")
    
    # Import and run the agent
    from root_agent.agent import app, root_agent
    
    if app:
        import uvicorn
        port = int(os.getenv("PORT", 8000))
        print(f"🚀 Server starting on http://0.0.0.0:{port}")
        print(f"📡 Agent ready to handle requests!\n")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("✅ Root agent loaded successfully")
        print(f"   Agent name: {root_agent.name if hasattr(root_agent, 'name') else root_agent._name}")
        print(f"   Tools: {len(root_agent._tools if hasattr(root_agent, '_tools') else root_agent.tools)}")
        print("\nNote: FastAPI not available. Install with: pip install fastapi uvicorn")
