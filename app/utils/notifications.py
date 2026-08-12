import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def log_activity(user_id: int, action: str):
    """Log user activity."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} | User: {user_id} | Action: {action}\n"
    print(f"[ACTIVITY] User {user_id} performed action: {action}")

    with (PROJECT_ROOT / "activity_log.txt").open("a", encoding="utf-8") as f:
        f.write(entry)


def send_notification(email: str, message: str):
    """Simulate sending a notification (slow operation)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[NOTIFICATION] Sending to {email}...")
    time.sleep(2)  # Simulate network delay
    print(f"[NOTIFICATION] Sent: '{message}' to {email}")

    with (PROJECT_ROOT / "notification_log.txt").open("a", encoding="utf-8") as f:
        f.write(f"{timestamp} | To: {email} | Message: {message}\n")
