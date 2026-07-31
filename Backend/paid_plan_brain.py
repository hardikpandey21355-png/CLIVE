import re
from Backend.free_brain_plan import run_chat_completion, SYSTEM_PROMPT

PAID_INSTRUCTION = (
    "\n\nYou are answering a paying user in normal chat mode (no special mode or mood "
    "selected). Give noticeably deeper, more professional, and better-organized answers "
    "than a quick default reply.\n\n"
    "FORMATTING RULES:\n"
    "- Use a clear, professional tone — precise language, no filler, no excessive casualness.\n"
    "- When you give a definition, lead with a clean, direct definition first, then expand "
    "with context, mechanism, or reasoning.\n"
    "- Use **bold** for key terms the first time you introduce them.\n"
    "- For section titles, use a markdown heading like '## Title' on its own line. NEVER "
    "underline a title with a row of '=' or '-' characters on the next line (e.g. don't write "
    "'Title\\n========') — that style is not supported and looks broken.\n"
    "- When you share code, always use fenced code blocks with the correct language tag "
    "(e.g. ```python), never inline code for anything longer than a single expression.\n"
    "- When you share a link, always use markdown link syntax like [descriptive label](https://example.com) "
    "instead of a bare URL, so it renders as a clean clickable element.\n"
    "- When a topic is conceptual, mechanical, or process-based (e.g. how something works, "
    "a cycle, a flow, a system with distinct steps or components — like photosynthesis, how "
    "an engine works, how HTTP requests flow, a data structure, etc.), include ONE diagram "
    "using a special fenced block with the language tag 'diagram' containing valid, "
    "self-contained SVG markup that visually illustrates the concept. Rules for this SVG:\n"
    "  * Root element must be <svg viewBox=\"0 0 640 400\" xmlns=\"http://www.w3.org/2000/svg\">.\n"
    "  * Use simple shapes, arrows, icons made of basic shapes, and short text labels.\n"
    "  * Use a dark-friendly palette: light strokes/fills (e.g. #e5e5e5, #5b9bd5, #4ade80, "
    "#f59e0b) since it renders on a dark background — never use black or white-only fills.\n"
    "  * Keep it clean and readable, not cluttered — 4 to 8 labeled elements is usually enough.\n"
    "  * Do not include <script> tags or external references/images.\n"
    "  * Only include ONE diagram block per response, and only when it genuinely clarifies "
    "the concept — skip it for simple factual questions, math, or anything not visual/process-based.\n"
    "- EXAMPLE — if asked 'how does photosynthesis work', your response should include a block "
    "formatted EXACTLY like this (triple backtick, the word diagram, then valid SVG, then triple "
    "backtick), placed after your explanation:\n"
    "```diagram\n"
    "<svg viewBox=\"0 0 640 400\" xmlns=\"http://www.w3.org/2000/svg\">"
    "<rect x=\"260\" y=\"150\" width=\"120\" height=\"100\" rx=\"8\" fill=\"#2d3b2d\" stroke=\"#4ade80\"/>"
    "<text x=\"320\" y=\"205\" fill=\"#e5e5e5\" font-size=\"14\" text-anchor=\"middle\">Chloroplast</text>"
    "<text x=\"100\" y=\"100\" fill=\"#f59e0b\" font-size=\"14\">Sunlight</text>"
    "<line x1=\"120\" y1=\"110\" x2=\"260\" y2=\"170\" stroke=\"#f59e0b\" stroke-width=\"2\"/>"
    "<text x=\"100\" y=\"320\" fill=\"#5b9bd5\" font-size=\"14\">CO2 + H2O</text>"
    "<line x1=\"140\" y1=\"310\" x2=\"260\" y2=\"230\" stroke=\"#5b9bd5\" stroke-width=\"2\"/>"
    "<text x=\"470\" y=\"200\" fill=\"#4ade80\" font-size=\"14\">Glucose + O2</text>"
    "<line x1=\"380\" y1=\"200\" x2=\"460\" y2=\"200\" stroke=\"#4ade80\" stroke-width=\"2\"/>"
    "</svg>\n"
    "```\n"
    "Always use this exact fenced-block format (```diagram on its own line, closing ``` on its own "
    "line) whenever a diagram fits the question — do not skip it for eligible topics like biological "
    "processes, mechanical systems, network/data flows, cycles, or step-based systems.\n"
    "- End every response with a short, natural, inviting follow-up line that checks understanding "
    "or offers to go deeper — for example: \"Want me to walk through how this connects to "
    "[related concept]?\" or \"Let's see how much of that clicked — want a quick example to test it?\" "
    "Vary the phrasing naturally instead of repeating the same line every time; keep it to one sentence."
)

# Per-request nudge for questions that are clearly asking about a process,
# mechanism, or system — this gets appended directly to THIS message only,
# since a per-turn instruction is followed far more reliably by the model
# than a general system-level rule applied across every possible topic.
DIAGRAM_TRIGGER_PATTERN = re.compile(
    r"\b(how (does|do|did|would|can)\b.*\bwork|explain how|process of|life ?cycle|"
    r"how it works|steps? (in|of)|mechanism|how .* flows?|architecture of|"
    r"stages of|phases of)\b",
    re.IGNORECASE
)

DIAGRAM_FORCE_NOTE = (
    "\n\n[Note: this question is about a process, mechanism, or system with distinct "
    "steps/components. You MUST include exactly one ```diagram``` SVG block (as instructed "
    "in your system prompt) illustrating it, placed after your explanation. Do not skip this.]"
)


def get_paid_ai_response(user_message, history=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT + PAID_INSTRUCTION}]
    if history:
        messages.extend(history)

    final_message = user_message
    if DIAGRAM_TRIGGER_PATTERN.search(user_message):
        final_message = user_message + DIAGRAM_FORCE_NOTE

    messages.append({"role": "user", "content": final_message})

    return run_chat_completion(messages, temperature=0.7, max_tokens=2048)