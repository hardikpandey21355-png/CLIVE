import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found. Check your .env file.")

client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are Clive, a helpful, friendly AI assistant. "
    "Keep answers clear and to the point."
)


def generate_chat_title(user_message, ai_message):
    """
    Looks at the first exchange (user + AI reply) and asks the model
    to summarize it into a short chat title.
    """
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
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
        ],
        temperature=0.5,
        max_tokens=20,
    )
    return completion.choices[0].message.content.strip().strip('"')



def get_ai_response(user_message, history=None):
    """
    user_message: str - latest message from the user
    history: list of {"role": "user"/"assistant", "content": "..."}
    Returns: str - the AI's reply text
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": user_message})

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )

    return completion.choices[0].message.content

