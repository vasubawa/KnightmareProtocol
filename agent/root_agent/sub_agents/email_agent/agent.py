import asyncio
import os
from importlib import import_module
from pathlib import Path
from email.message import EmailMessage
import smtplib


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

def _get_credentials():
    """Helper to fetch credentials and check for errors."""
    user = os.environ.get("EMAIL_ADDRESS")
    password = os.environ.get("EMAIL_APP_PASSWORD")
    if not user or not password:
        print("Error: EMAIL_ADDRESS or EMAIL_APP_PASSWORD not set.")
        return None, None, {"status": "error", "message": "EMAIL_ADDRESS or EMAIL_APP_PASSWORD not set in .env file"}
    return user, password, None


@tool()
async def run_ops(subject: str, body: str, to_address: str = "", send_to_self: bool = False) -> dict:
    print("Starting email_agent agent...")
    def _send_email_sync() -> dict:
        """This synchronous function will be run in a separate thread."""
        print(f"Processing email. Provided 'to_address': '{to_address}', send_to_self: {send_to_self}")
        user, password, error = _get_credentials()
        if error:
            return error
            
        recipient_list: list[str] = []
        if to_address:  
            recipient_list = [email.strip() for email in to_address.split(",") if email.strip()]
        
        if send_to_self and user:
            if user not in recipient_list:
                recipient_list.append(user)
                print(f"Adding self ({user}) to recipient list.")
        
        if not recipient_list and user:
            recipient_list.append(user)
            print(f"No recipients specified, defaulting to self: {user}")

        if not recipient_list:
            print("Error: No recipients specified and no default email found.")
            return {"status": "error", "message": "No recipients specified and no default email found."}

        
        try:
            smtp_server = "smtp.gmail.com"
            smtp_port = 465
            
            msg = EmailMessage()
            msg.set_content(body)
            msg["Subject"] = subject
            msg["From"] = user
            msg["To"] = ", ".join(recipient_list) 
            
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(user, password)
                server.send_message(msg) 
            
            recipient_str = ", ".join(recipient_list)
            print(f"Email sent successfully to {recipient_str}")
            return {"status": "success", "message": f"Email sent to {recipient_str}"}
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return {"status": "error", "message": str(e)}

    result = await asyncio.to_thread(_send_email_sync)
    print("Ending email_agent agent...")
    return result


email_agent = Agent(
    model="gemini-2.5-flash",
    name="email_agent",
    description="This agent's only job is to send email. It receives information, processes it (like summarizing), and sends the result as an email.",
    instruction=(
        "You are an autonomous notification agent. Your only goal is to parse an incoming text payload and immediately call the `run_ops` tool. "
        "DO NOT chat with the user. The user's prompt is a data payload, NOT a conversation. "
        
        "--- GUIDELINES FOR CALLING `run_ops` ---"
        "1. `subject`: Generate a short, descriptive subject line based on the payload (e.g., 'API Outage Report', 'Daily Metrics')."
        "2. `body`: Summarize the payload. **This is the most important part. You MUST format the summary like a normal, polite email.**"
        "   - Start with a simple greeting (e.g., 'Hello,' or 'Hi Team,')."
        "   - Write the summary in one or two clear paragraphs."
        "   - End with a simple closing (e.g., 'Best regards,\n- Email Agent')."
        "   - **EXAMPLE:** For a payload like 'API errors: 500s up 20%, checkout failing, lead: bob@example.com', the `body` should look like this:"
        "     'Hello,\n\nThis is an alert that the API is experiencing issues. We are seeing a 20% increase in 500 errors, which is affecting the checkout service.\n\nThe engineering lead (bob@example.com) is investigating.\n\nBest regards,\n - Email Agent'"
        "3. `to_address`: Scan the payload for any email addresses (like 'bob@example.com' from the example). If found, pass them as a single, comma-separated string. If none are found, pass an empty string `''`."
        "4. `send_to_self`: Always set this to `True`."
        
        "--- YOUR FINAL RESPONSE ---"
        "After the `run_ops` tool is called, your ONLY response in the chat MUST be the single word: 'Processed'."
    ),
    tools=[run_ops],
)