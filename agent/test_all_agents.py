#!/usr/bin/env python3
"""
Comprehensive Agent Testing Script
Tests all agents in the system and reports their status
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_section(title):
    """Print a test section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_result(name, success, message=""):
    """Print a test result"""
    status = "✓" if success else "✗"
    color = "\033[92m" if success else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} {name:<40} {message}")

def get_agent_info(agent):
    """Get info from agent (works with both real LlmAgent and fallback)"""
    if hasattr(agent, 'config'):
        # Fallback agent
        return {
            'name': agent.config.get('name', 'Unknown'),
            'tools': agent.config.get('tools', [])
        }
    else:
        # Real LlmAgent
        return {
            'name': getattr(agent, 'name', getattr(agent, '_name', 'Unknown')),
            'tools': getattr(agent, 'tools', getattr(agent, '_tools', []))
        }


# ============================================================================
# TEST DEV AGENTS
# ============================================================================
def test_dev_agents():
    test_section("Development Agents")
    
    # Test doc_agent
    try:
        from root_agent.dev_agent.doc_agent.agent import root_agent as doc_agent
        info = get_agent_info(doc_agent)
        test_result("doc_agent", True, f"Tools: {len(info['tools'])}")
    except Exception as e:
        test_result("doc_agent", False, str(e)[:50])
    
    # Test linter_agent
    try:
        from root_agent.dev_agent.linter_agent.agent import root_agent as linter_agent
        info = get_agent_info(linter_agent)
        test_result("linter_agent", True, f"Tools: {len(info['tools'])}")
    except Exception as e:
        test_result("linter_agent", False, str(e)[:50])
    
    # Test testing_agent
    try:
        from root_agent.dev_agent.testing_agent.agent import root_agent as testing_agent
        info = get_agent_info(testing_agent)
        test_result("testing_agent", True, f"Tools: {len(info['tools'])}")
    except Exception as e:
        test_result("testing_agent", False, str(e)[:50])

# ============================================================================
# TEST SUB AGENTS
# ============================================================================
def test_sub_agents():
    test_section("Sub Agents")
    
    agents_to_test = [
        ("calendar_agent", "root_agent.sub_agents.calendar_agent.agent", "calendar_agent"),
        ("commute_agent", "root_agent.sub_agents.commute_agent.agent", "commute_agent"),
        ("critic_agent", "root_agent.sub_agents.critic_agent.agent", "critic_agent"),
        ("email_agent", "root_agent.sub_agents.email_agent.agent", "email_agent"),
        ("flight_agent", "root_agent.sub_agents.flight_agent.agent", "flight_agent"),
        ("focus_agent", "root_agent.sub_agents.focus_agent.agent", "focus_agent"),
        ("knowledge_agent", "root_agent.sub_agents.knowledge_agent.agent", "knowledge_agent"),
        ("memory_agent", "root_agent.sub_agents.memory_agent.agent", "memory_agent"),
        ("notification_agent", "root_agent.sub_agents.notification_agent.agent", "notification_agent"),
        ("planner_agent", "root_agent.sub_agents.planner_agent.agent", "planner_agent"),
        ("wellness_agent", "root_agent.sub_agents.wellness_agent.agent", "wellness_agent"),
    ]
    
    for display_name, module_path, agent_name in agents_to_test:
        try:
            module = __import__(module_path, fromlist=[agent_name])
            agent = getattr(module, agent_name)
            info = get_agent_info(agent)
            tools_count = len(info['tools'])
            test_result(display_name, True, f"Tools: {tools_count}")
        except Exception as e:
            test_result(display_name, False, str(e)[:50])

# ============================================================================
# TEST AGENT TOOLS
# ============================================================================
async def test_agent_tools():
    test_section("Agent Tools Functionality")
    
    # Test memory_agent tools
    try:
        from root_agent.sub_agents.memory_agent.agent import memory_agent
        info = get_agent_info(memory_agent)
        store_tool = info['tools'][0]
        get_tool = info['tools'][1]
        
        # Store a value
        result = await store_tool("test_user", "test_key", "test_value")
        store_success = "Stored" in str(result)
        
        # Retrieve the value
        result = await get_tool("test_user", "test_key")
        get_success = "test_value" in str(result)
        
        test_result("memory_agent.store_preference", store_success)
        test_result("memory_agent.get_preference", get_success)
    except Exception as e:
        test_result("memory_agent tools", False, str(e)[:50])
    
    # Test notification_agent tools
    try:
        from root_agent.sub_agents.notification_agent.agent import notification_agent
        info = get_agent_info(notification_agent)
        send_tool = info['tools'][0]
        
        result = await send_tool("Test", "Test message", "normal")
        success = "sent" in str(result).lower()
        test_result("notification_agent.send_notification", success)
    except Exception as e:
        test_result("notification_agent tools", False, str(e)[:50])
    
    # Test knowledge_agent tools
    try:
        from root_agent.sub_agents.knowledge_agent.agent import knowledge_agent
        info = get_agent_info(knowledge_agent)
        search_tool = info['tools'][0]
        
        result = await search_tool("Python programming")
        success = len(str(result)) > 10
        test_result("knowledge_agent.run_ops", success, "Wikipedia query")
    except Exception as e:
        test_result("knowledge_agent tools", False, str(e)[:50])
    
    # Test email_agent (will fail without credentials)
    try:
        from root_agent.sub_agents.email_agent.agent import email_agent
        info = get_agent_info(email_agent)
        email_tool = info['tools'][0]
        
        result = await email_tool("Test", "Test body", "", True)
        has_error = "error" in str(result).lower()
        test_result("email_agent.run_ops", has_error, "Expected credential error")
    except Exception as e:
        test_result("email_agent tools", False, str(e)[:50])
    
    # Test doc_agent tools
    try:
        from root_agent.dev_agent.doc_agent.agent import root_agent as doc_agent
        info = get_agent_info(doc_agent)
        analyze_tool = info['tools'][0]
        
        # Analyze this file
        result = await analyze_tool(__file__)
        success = "Documentation Analysis" in str(result)
        test_result("doc_agent.analyze_python_file", success)
    except Exception as e:
        test_result("doc_agent tools", False, str(e)[:50])
    
    # Test linter_agent tools
    try:
        from root_agent.dev_agent.linter_agent.agent import root_agent as linter_agent
        info = get_agent_info(linter_agent)
        syntax_tool = info['tools'][0]
        
        result = await syntax_tool(__file__)
        success = "valid Python syntax" in str(result) or "✓" in str(result)
        test_result("linter_agent.check_python_syntax", success)
    except Exception as e:
        test_result("linter_agent tools", False, str(e)[:50])

# ============================================================================
# TEST ROOT AGENTS
# ============================================================================
def test_root_agents():
    test_section("Root Orchestrator Agents")
    
    # Test main root_agent
    try:
        from root_agent.agent import root_agent
        info = get_agent_info(root_agent)
        tools_count = len(info['tools'])
        test_result("root_agent (orchestrator)", True, f"Tools: {tools_count}")
    except Exception as e:
        test_result("root_agent (orchestrator)", False, str(e)[:50])
    
    # Test sub_agents orchestrator
    try:
        from root_agent.sub_agents.agent import root_agent as workflow_agent
        if workflow_agent:
            # Try to get sub_agents from the agent
            sub_agents = getattr(workflow_agent, 'sub_agents', getattr(workflow_agent, '_sub_agents', []))
            test_result("workflow_agent (parallel/sequential)", True, f"Sub-agents: {len(sub_agents)}")
        else:
            test_result("workflow_agent (parallel/sequential)", False, "Agent is None")
    except Exception as e:
        test_result("workflow_agent (parallel/sequential)", False, str(e)[:50])

# ============================================================================
# TEST IMPORTS
# ============================================================================
def test_imports():
    test_section("Module Imports")
    
    # Test dev_agent package import
    try:
        from root_agent.dev_agent import doc_agent, linter_agent, testing_agent
        test_result("dev_agent package", True, "All 3 agents imported")
    except Exception as e:
        test_result("dev_agent package", False, str(e)[:50])
    
    # Test sub_agents package import
    try:
        from root_agent.sub_agents import (
            calendar_agent,
            commute_agent,
            critic_agent,
            email_agent,
            flight_agent,
            focus_agent,
            knowledge_agent,
            memory_agent,
            notification_agent,
            planner_agent,
            wellness_agent,
        )
        test_result("sub_agents package", True, "All 11 agents imported")
    except Exception as e:
        test_result("sub_agents package", False, str(e)[:50])

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
def main():
    print("\n" + "="*60)
    print(" AGENT SYSTEM COMPREHENSIVE TEST")
    print("="*60)
    
    # Run synchronous tests
    test_imports()
    test_dev_agents()
    test_sub_agents()
    test_root_agents()
    
    # Run async tests
    print("\n")
    asyncio.run(test_agent_tools())
    
    # Summary
    print("\n" + "="*60)
    print(" TEST COMPLETE")
    print("="*60)
    print("\nℹ️  Note: Some agents may show 'Expected credential error' - this is normal")
    print("   if API keys are not configured in .env file.")
    print("\n")

if __name__ == "__main__":
    main()
