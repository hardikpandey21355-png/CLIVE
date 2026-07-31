import re
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

TIME_PATTERNS = [
    r"\bcurrent time\b",
    r"\bwhat time is it\b",
    r"\btime right now\b",
    r"\bwhat'?s the time\b",
]

DATE_PATTERNS = [
    r"\bcurrent date\b",
    r"\btoday'?s date\b",
    r"\bwhat'?s today'?s date\b",
    r"\bwhat day is it\b",
    r"\bwhat is the date\b",
]

def check_live_time_question(user_message):
    """
    Returns a direct answer string if user_message is a simple time/date
    question, otherwise returns None so the caller falls through to
    normal AI/search handling.
    """
    text = user_message.lower()

    for pattern in TIME_PATTERNS:
        if re.search(pattern, text):
            now = datetime.now(IST)
            return f"Right now it's {now.strftime('%I:%M %p')} (IST), on {now.strftime('%A, %B %d, %Y')}."

    for pattern in DATE_PATTERNS:
        if re.search(pattern, text):
            now = datetime.now(IST)
            return f"Today's date is {now.strftime('%A, %B %d, %Y')}."

    return None