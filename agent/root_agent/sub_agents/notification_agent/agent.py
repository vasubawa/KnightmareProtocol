"""
Notification Agent - Sends alerts, reminders, and status updates
"""
import asyncio
import os
import json
from datetime import datetime
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


# Notification store
NOTIFICATION_FILE = Path(__file__).parent / "notifications.json"


def _load_notifications():
    """Load notifications from file."""
    if NOTIFICATION_FILE.exists():
        with open(NOTIFICATION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_notifications(notifications):
    """Save notifications to file."""
    with open(NOTIFICATION_FILE, "w", encoding="utf-8") as f:
        json.dump(notifications, f, indent=2)


@tool()
async def send_notification(title: str, message: str, priority: str = "normal") -> str:
    """
    Send a notification and store it.
    
    Args:
        title: Notification title
        message: Notification message
        priority: Priority level (low, normal, high, urgent)
    """
    notification = {
        "id": datetime.now().isoformat(),
        "title": title,
        "message": message,
        "priority": priority,
        "timestamp": datetime.now().isoformat(),
        "read": False
    }
    
    notifications = _load_notifications()
    notifications.append(notification)
    _save_notifications(notifications)
    
    print(f"📬 Notification: [{priority.upper()}] {title}")
    print(f"   {message}")
    
    return f"Notification sent: {title}"


@tool()
async def get_notifications(unread_only: bool = False) -> str:
    """
    Get all notifications or only unread ones.
    
    Args:
        unread_only: If True, only return unread notifications
    """
    notifications = _load_notifications()
    
    if unread_only:
        notifications = [n for n in notifications if not n.get("read", False)]
    
    if not notifications:
        return "No notifications."
    
    result = []
    for notif in notifications[-10:]:  # Last 10
        status = "📭 UNREAD" if not notif.get("read", False) else "📬 Read"
        result.append(f"{status} [{notif.get('priority', 'normal').upper()}] {notif['title']}")
        result.append(f"   {notif['message']}")
        result.append(f"   Time: {notif['timestamp']}")
        result.append("")
    
    return "\n".join(result)


@tool()
async def mark_notification_read(notification_id: str) -> str:
    """Mark a notification as read."""
    notifications = _load_notifications()
    
    for notif in notifications:
        if notif["id"] == notification_id:
            notif["read"] = True
            _save_notifications(notifications)
            return f"Notification {notification_id} marked as read."
    
    return f"Notification {notification_id} not found."


@tool()
async def clear_notifications(keep_unread: bool = True) -> str:
    """
    Clear notifications.
    
    Args:
        keep_unread: If True, keep unread notifications
    """
    if keep_unread:
        notifications = _load_notifications()
        unread = [n for n in notifications if not n.get("read", False)]
        _save_notifications(unread)
        return f"Cleared read notifications. {len(unread)} unread notifications remain."
    else:
        _save_notifications([])
        return "All notifications cleared."


@tool()
async def schedule_reminder(title: str, message: str, delay_seconds: int = 60) -> str:
    """
    Schedule a reminder notification.
    
    Args:
        title: Reminder title
        message: Reminder message
        delay_seconds: Delay in seconds before notification
    """
    await asyncio.sleep(delay_seconds)
    await send_notification(f"⏰ Reminder: {title}", message, "high")
    return f"Reminder scheduled for {delay_seconds} seconds from now."


notification_agent = Agent(
    model="gemini-2.5-flash",
    name="notification_agent",
    description="Sends alerts, reminders, and status updates to stakeholders.",
    instruction="Orchestrate timely notifications, manage notification history, and tailor messaging to user context. Send important updates with appropriate priority levels.",
    tools=[send_notification, get_notifications, mark_notification_read, clear_notifications, schedule_reminder],
)
