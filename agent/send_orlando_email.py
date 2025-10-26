#!/usr/bin/env python3
"""
Simple script to send an email with Orlando facts using the agents
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def send_orlando_email():
    """Send an email with Orlando facts"""
    
    # Import the agents
    from root_agent.sub_agents.email_agent.agent import email_agent
    from root_agent.sub_agents.knowledge_agent.agent import knowledge_agent
    
    print("🔍 Fetching Orlando facts from Wikipedia...")
    
    # Get the knowledge agent tool
    knowledge_tools = knowledge_agent._tools if hasattr(knowledge_agent, '_tools') else knowledge_agent.tools
    search_tool = knowledge_tools[0]
    
    # Fetch Orlando facts
    orlando_info = await search_tool("Orlando Florida")
    
    print(f"\n📝 Found information:\n{orlando_info[:300]}...\n")
    
    # Get the email agent tool
    email_tools = email_agent._tools if hasattr(email_agent, '_tools') else email_agent.tools
    send_email_tool = email_tools[0]
    
    # Compose and send the email
    print("📧 Sending email with Orlando facts...\n")
    
    result = await send_email_tool(
        subject="Interesting Facts About Orlando, Florida",
        body=f"Hello!\n\nHere are some fascinating facts about Orlando, Florida:\n\n{orlando_info}\n\nEnjoy learning about this amazing city!\n\nBest regards,\nYour AI Agent System",
        to_address="",  # Leave empty to send to yourself
        send_to_self=True
    )
    
    print(f"\n✅ Result: {result}\n")
    
    if result.get('status') == 'success':
        print("🎉 Email sent successfully!")
    else:
        print(f"⚠️  Issue: {result.get('message')}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" SENDING ORLANDO FACTS EMAIL")
    print("="*60 + "\n")
    
    asyncio.run(send_orlando_email())
    
    print("\n" + "="*60)
    print(" DONE")
    print("="*60 + "\n")
