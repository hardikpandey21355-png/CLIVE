import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def _load_groq_keys():
    """Collects GROQ_API_KEY, GROQ_API_KEY_1, GROQ_API_KEY_2, ... from .env,
    in order, skipping duplicates."""
    keys = []
    primary = os.getenv("GROQ_API_KEY")
    if primary:
        keys.append(primary)

    i = 1
    while True:
        k = os.getenv(f"GROQ_API_KEY_{i}")
        if not k:
            break
        keys.append(k)
        i += 1

    seen = set()
    unique_keys = []
    for k in keys:
        if k not in seen:
            unique_keys.append(k)
            seen.add(k)
    return unique_keys


GROQ_KEYS = _load_groq_keys()
if not GROQ_KEYS:
    raise RuntimeError(
        "No Groq API keys found. Add GROQ_API_KEY (and optionally "
        "GROQ_API_KEY_1, GROQ_API_KEY_2, ...) to your .env file."
    )

# One Groq client per key, tried in order on every request
groq_clients = [Groq(api_key=k) for k in GROQ_KEYS]

# Kept for backward compatibility — some files import `client` directly
client = groq_clients[0]

GROQ_VOICE_API_KEY = os.getenv("GROQ_VOICE_API_KEY") or GROQ_KEYS[0]
voice_client = Groq(api_key=GROQ_VOICE_API_KEY)

MODEL_NAME = "llama-3.3-70b-versatile"
VOICE_MODEL_NAME = "llama-3.1-8b-instant"

print(f"DEBUG — Loaded {len(GROQ_KEYS)} Groq API key(s) for rotation.")

PERSONA_DIR = os.path.join(os.path.dirname(__file__), "persona")


def _load_persona_file(filename):
    path = os.path.join(PERSONA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


PERSONALITY_TEXT = _load_persona_file("personality.txt")
RULES_TEXT = _load_persona_file("rules.txt")
RESPONSE_FORMAT_TEXT = _load_persona_file("response_format.txt")

SYSTEM_PROMPT = "\n\n".join(
    part for part in [PERSONALITY_TEXT, RULES_TEXT, RESPONSE_FORMAT_TEXT] if part
) or (
    "You are Clive, a helpful, friendly AI assistant created by a B.Tech CSE "
    "student named Hardik Pandey. Keep answers clear and to the point."
)


def run_chat_completion(messages, temperature=0.7, max_tokens=1024,
                         groq_client=None, groq_model=None):
    """
    Tries every configured Groq key in order (or a single explicit
    groq_client if one is passed in, e.g. for voice). Rotates to the
    next key automatically on rate-limit / error. Raises the last
    error if every key fails.
    """
    groq_model = groq_model or MODEL_NAME
    clients_to_try = [groq_client] if groq_client else groq_clients

    last_error = None
    for idx, gc in enumerate(clients_to_try):
        try:
            completion = gc.chat.completions.create(
                model=groq_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            if idx > 0:
                print(f"DEBUG — Recovered using Groq key #{idx + 1}")
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq key #{idx + 1} failed (model={groq_model}):", e)
            last_error = e
            continue  # rotate to the next Groq key

    # every available Groq key failed
    raise last_error


def generate_chat_title(user_message, ai_message):
    """
    Looks at the first exchange (user + AI reply) and asks the model
    to summarize it into a short chat title. Also rotates across keys.
    """
    messages = [
        {
            "role": "system",
            "content": "You generate short chat titles (3-6 words). "
                       "Reply with ONLY the title text — no quotes, "
                       "no punctuation at the end, nothing else."
        },
        {
            "role": "user",
            "content": f"User: {user_message}\nAssistant: {ai_message}\n\nTitle:"
        }
    ]
    title = run_chat_completion(messages, temperature=0.5, max_tokens=20)
    return title.strip().strip('"')


def get_ai_response(user_message, history=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    return run_chat_completion(messages, temperature=0.7, max_tokens=1024)


def get_voice_ai_response(user_message, history=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    return run_chat_completion(
        messages,
        temperature=0.7,
        max_tokens=512,
        groq_client=voice_client,
        groq_model=VOICE_MODEL_NAME,
    )