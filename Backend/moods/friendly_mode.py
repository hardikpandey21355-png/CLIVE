from Backend.free_brain_plan import run_chat_completion, SYSTEM_PROMPT

FRIENDLY_INSTRUCTION = (
    "\n\nYou are in Friendly mode. Talk warmly and casually, like a close friend "
    "chatting rather than an assistant giving a formal answer. Still be accurate "
    "and helpful — just keep the tone relaxed, encouraging, and personal."
)

def get_friendly_response(user_message, history=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT + FRIENDLY_INSTRUCTION}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    return run_chat_completion(messages, temperature=0.8, max_tokens=1024)