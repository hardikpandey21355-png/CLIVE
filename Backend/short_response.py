from Backend.free_brain_plan import run_chat_completion, SYSTEM_PROMPT

SHORT_RESPONSE_INSTRUCTION = (
    "\n\nYou are in Short Response mode. Answer in 1-3 sentences maximum. "
    "No headings, no bullet lists, no elaboration beyond what's directly asked."
)

def get_short_response(user_message, history=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT + SHORT_RESPONSE_INSTRUCTION}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    return run_chat_completion(messages, temperature=0.6, max_tokens=200)