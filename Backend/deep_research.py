from Backend.free_brain_plan import run_chat_completion, SYSTEM_PROMPT
from Backend.live_time import check_live_time_question
from Backend.web_search import tavily_client, _format_search_results

DEEP_RESEARCH_INSTRUCTION = (
    "\n\nYou are in Deep Research mode. Give a thorough, well-structured answer "
    "using the multiple web search results provided below. Use headings to "
    "organize distinct aspects of the topic, and cite sources naturally by name."
)

def _generate_subqueries(user_message):
    prompt = (
        f"Break the following question into 2-4 distinct, specific web search "
        f"queries that together would gather enough information to answer it "
        f"thoroughly. Reply with ONLY the queries, one per line, no numbering.\n\n"
        f"Question: {user_message}"
    )
    raw = run_chat_completion(
        [
            {"role": "system", "content": "You generate concise, targeted web search queries."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=150,
    ).strip()
    queries = [q.strip("-• ").strip() for q in raw.split("\n") if q.strip()]
    return queries[:4] if queries else [user_message]


def get_deep_research_response(user_message, history=None):
    live_answer = check_live_time_question(user_message)
    if live_answer:
        return live_answer

    if not tavily_client:
        return "Deep Research isn't configured yet — missing TAVILY_API_KEY."

    try:
        subqueries = _generate_subqueries(user_message)
    except Exception as e:
        print("Subquery generation failed:", e)
        subqueries = [user_message]

    all_context_blocks = []
    for q in subqueries:
        try:
            result = tavily_client.search(query=q, max_results=4)
            block = _format_search_results(result.get("results", []))
            all_context_blocks.append(f"Search: {q}\n{block}")
        except Exception as e:
            print("Tavily search error for subquery:", q, e)

    combined_context = "\n\n---\n\n".join(all_context_blocks) or "No search results found."

    messages = [{"role": "system", "content": SYSTEM_PROMPT + DEEP_RESEARCH_INSTRUCTION}]
    if history:
        messages.extend(history)
    messages.append({
        "role": "user",
        "content": f"{user_message}\n\n[Combined web research:]\n{combined_context}"
    })

    return run_chat_completion(messages, temperature=0.5, max_tokens=1500)