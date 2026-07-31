import os
from tavily import TavilyClient
from Backend.free_brain_plan import run_chat_completion, SYSTEM_PROMPT
from Backend.live_time import check_live_time_question

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None

WEB_SEARCH_INSTRUCTION = (
    "\n\nYou are in Web Search mode. You have been given fresh web search results "
    "below as context. Use them to answer the user's question accurately, citing "
    "sources naturally by name (e.g. 'according to [source]') where relevant. "
    "If the search results don't answer the question, say so honestly instead of guessing."
)

def _format_search_results(results):
    if not results:
        return "No relevant search results were found."
    blocks = []
    for r in results[:5]:
        title = r.get("title", "Untitled")
        url = r.get("url", "")
        content = r.get("content", "")[:800]
        blocks.append(f"Source: {title} ({url})\n{content}")
    return "\n\n".join(blocks)


def get_web_search_response(user_message, history=None):
    live_answer = check_live_time_question(user_message)
    if live_answer:
        return live_answer

    if not tavily_client:
        return "Web Search isn't configured yet — missing TAVILY_API_KEY."

    try:
        search_result = tavily_client.search(query=user_message, max_results=5)
        results = search_result.get("results", [])
    except Exception as e:
        print("Tavily search error:", e)
        return "Sorry, I couldn't reach the web search service right now."

    context_block = _format_search_results(results)

    messages = [{"role": "system", "content": SYSTEM_PROMPT + WEB_SEARCH_INSTRUCTION}]
    if history:
        messages.extend(history)
    messages.append({
        "role": "user",
        "content": f"{user_message}\n\n[Web search results:]\n{context_block}"
    })

    return run_chat_completion(messages, temperature=0.5, max_tokens=1024)