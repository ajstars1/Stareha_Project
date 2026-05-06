"""
Desktop notification helper — Stage 6.

Uses notify-send (libnotify) on Linux. Silently skips if unavailable.
Never raises — notifications are best-effort, never blocking.
"""
import subprocess
from typing import Literal

Urgency = Literal["low", "normal", "critical"]


def notify(title: str, body: str = "", urgency: Urgency = "normal",
           icon: str = "dialog-information") -> None:
    """Send a desktop notification. Silently skips if notify-send is unavailable."""
    try:
        args = [
            "notify-send",
            "--app-name=Stareha",
            f"--urgency={urgency}",
            f"--icon={icon}",
            title,
        ]
        if body:
            args.append(body)
        subprocess.run(args, capture_output=True, timeout=3)
    except Exception:
        pass


def notify_inbox(count: int) -> None:
    if count == 1:
        notify("Stareha · 1 new memory", "Run `stareha memory inbox` to review.")
    elif count > 1:
        notify(f"Stareha · {count} new memories", "Run `stareha memory inbox` to review.")


def notify_briefing_ready() -> None:
    notify("Stareha · Briefing ready",
           "Run `stareha brief` or open the companion panel.", urgency="low")


def notify_session_started(goal: str) -> None:
    notify("Stareha · Session started", goal or "No goal set", urgency="low")


def notify_session_ended(duration_min: int) -> None:
    notify("Stareha · Session ended",
           f"{duration_min}m — learning run triggered.", urgency="low")


def is_available() -> bool:
    try:
        result = subprocess.run(["which", "notify-send"],
                                capture_output=True, timeout=2)
        return result.returncode == 0
    except Exception:
        return False
