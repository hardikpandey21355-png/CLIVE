import re

# Matches messages that are clearly asking about something time-sensitive /
# current, which the model's static knowledge can't answer reliably.
LIVE_INFO_PATTERN = re.compile(
    r"\b(latest|breaking|current(ly)?|today'?s?|this week'?s?|right now|live|"
    r"recent(ly)?|update on|happening now|news|headlines?|score|results?|"
    r"who won|stock price|share price|exchange rate|weather (today|now|"
    r"tomorrow)|election results?|current price|trending)\b",
    re.IGNORECASE
)

# Messages that look like they need MULTIPLE angles researched, not just
# a single quick lookup — these get routed to Deep Research instead.
DEEP_RESEARCH_HINT_PATTERN = re.compile(
    r"\b(compare|comparison|pros and cons|in[- ]depth|detailed analysis|"
    r"research|report on|deep dive|explain in detail|everything about)\b",
    re.IGNORECASE
)


def needs_live_search(user_message):
    """True if the message needs fresh, real-world/current information."""
    if not user_message:
        return False
    return bool(LIVE_INFO_PATTERN.search(user_message))


def needs_deep_research(user_message):
    """True if a live-info question also looks like it needs multi-angle research."""
    if not user_message:
        return False
    return bool(DEEP_RESEARCH_HINT_PATTERN.search(user_message))