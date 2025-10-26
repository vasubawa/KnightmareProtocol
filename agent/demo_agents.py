#!/usr/bin/env python3
"""
Demo script showing how to use the agents
"""

import asyncio
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

async def demo_email_with_orlando_facts():
    """Send an email with random Orlando facts"""
    print("\n📧 Demo: Sending email with Orlando facts\n")
    
    from root_agent.sub_agents.email_agent.agent import email_agent
    from root_agent.sub_agents.knowledge_agent.agent import knowledge_agent
    
    # Get info from knowledge agent
    info = email_agent._tools if hasattr(email_agent, '_tools') else email_agent.tools
    email_tool = info[0]
    
    # Get Orlando facts
    knowledge_info = knowledge_agent._tools if hasattr(knowledge_agent, '_tools') else knowledge_agent.tools
    knowledge_tool = knowledge_info[0]
    
    print("🔍 Fetching Orlando facts from Wikipedia...")
    orlando_facts = await knowledge_tool("Orlando Florida")
    
    print(f"\n📝 Facts retrieved:\n{orlando_facts[:200]}...\n")
    
    # Send email
    print("📨 Sending email...")
    result = await email_tool(
        subject="Random Orlando Facts",
        body=f"Hello!\n\nHere are some interesting facts about Orlando, Florida:\n\n{orlando_facts}\n\nBest regards,\nYour Agent System",
        to_address="",
        send_to_self=True
    )
    
    print(f"\n✅ Email result: {result}\n")


async def demo_calendar():
    """Demonstrate calendar agent"""
    print("\n📅 Demo: Using Calendar Agent\n")
    
    from root_agent.sub_agents.calendar_agent.agent import calendar_agent
    
    # Get calendar info
    info = calendar_agent._tools if hasattr(calendar_agent, '_tools') else calendar_agent.tools
    
    print(f"Calendar Agent: {calendar_agent.name if hasattr(calendar_agent, 'name') else calendar_agent._name}")
    print(f"Description: {calendar_agent.description if hasattr(calendar_agent, 'description') else calendar_agent._description}")
    print(f"Available tools: {len(info)}")
    
    if info:
        print("\nCalling calendar tool...")
        calendar_tool = info[0]
        await calendar_tool()
    else:
        print("\nNote: Calendar agent currently has placeholder functionality.")
        print("To add real calendar features, you would integrate with Google Calendar API.")


async def demo_notification():
    """Send notifications"""
    print("\n🔔 Demo: Notification System\n")
    
    from root_agent.sub_agents.notification_agent.agent import notification_agent
    
    info = notification_agent._tools if hasattr(notification_agent, '_tools') else notification_agent.tools
    send_notif = info[0]
    get_notifs = info[1]
    
    # Send notifications
    print("Sending notifications...")
    await send_notif("Meeting Reminder", "Team meeting in 30 minutes", "high")
    await send_notif("Task Complete", "Code review finished", "normal")
    await send_notif("FYI", "New documentation available", "low")
    
    # Get notifications
    print("\nRetrieving notifications...")
    notifications = await get_notifs(unread_only=False)
    print(notifications)


async def demo_memory():
    """Demonstrate memory storage"""
    print("\n🧠 Demo: Memory Agent\n")
    
    from root_agent.sub_agents.memory_agent.agent import memory_agent
    
    info = memory_agent._tools if hasattr(memory_agent, '_tools') else memory_agent.tools
    store = info[0]
    get = info[1]
    
    # Store preferences
    print("Storing user preferences...")
    await store("user123", "favorite_city", "Orlando")
    await store("user123", "preferred_email_time", "9:00 AM")
    await store("user123", "theme", "dark")
    
    # Retrieve preferences
    print("\nRetrieving preferences...")
    city = await get("user123", "favorite_city")
    time = await get("user123", "preferred_email_time")
    theme = await get("user123", "theme")
    
    print(f"  Favorite City: {city}")
    print(f"  Preferred Email Time: {time}")
    print(f"  Theme: {theme}")


async def main():
    """Run all demos"""
    print("\n" + "="*60)
    print(" AGENT SYSTEM DEMOS")
    print("="*60)
    
    try:
        # Demo 1: Memory
        await demo_memory()
        
        # Demo 2: Notifications
        await demo_notification()
        
        # Demo 3: Calendar
        await demo_calendar()
        
        # Demo 4: Email with facts
        await demo_email_with_orlando_facts()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print(" DEMOS COMPLETE")
    print("="*60)
    print()


if __name__ == "__main__":
    asyncio.run(main())
