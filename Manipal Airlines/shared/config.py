"""
Shared configuration for Manipal Airlines agents.
In production, use environment variables for secrets.
"""
import os

# ── Google AI Studio ──────────────────────────────────────────────────────────
GOOGLE_API_KEY = os.environ.get(
    "GOOGLE_API_KEY",
    "",
)
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

# ── Scheduler ─────────────────────────────────────────────────────────────────
SCHEDULE_TIMEZONE = "Asia/Kolkata"
DAILY_FLIGHT_HOUR = 0       # Midnight — add next day's flights + clean expired
WEEKLY_LOYALTY_DAY = "mon"  # Monday
WEEKLY_LOYALTY_HOUR = 2     # 2 AM
DAILY_REPORT_HOUR = 6       # 6 AM
