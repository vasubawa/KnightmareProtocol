"""
Root Agent Package
Main orchestrator for the personal assistant system.
"""

try:
    from ..agent import root_agent
except (ImportError, ValueError):
    # Fallback for when imported as top-level module
    try:
        from agent import root_agent
    except ImportError:
        root_agent = None

__all__ = ["root_agent"]
