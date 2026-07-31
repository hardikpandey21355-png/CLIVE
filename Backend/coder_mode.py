from Backend.free_brain_plan import run_chat_completion, SYSTEM_PROMPT

CODER_INSTRUCTION = (
    "\n\nYou are in Coder mode. Prioritize correct, runnable, well-structured code. "
    "Default to best practices and idiomatic style for the language in question. "
    "Keep prose explanation brief and put it after the code block, not before, "
    "unless the user needs context first to understand the approach."
)

def get_coder_response(user_message, history=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT + CODER_INSTRUCTION}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    return run_chat_completion(messages, temperature=0.3, max_tokens=1500)