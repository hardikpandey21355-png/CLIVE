"""
project_files.py
-----------------
Handles reading the ACTUAL CONTENT of files attached to a Project (not just
their name/size, which is all projects.html currently stores).

This reuses the same extraction logic as file_reader.py (used for normal
chat attachments) so PDFs, DOCX, TXT, and CSV files all work the same way.

How this fits into the existing app:
- projects.html currently uploads files to the browser only (JS `File`
  objects held in memory), then discards them and just saves
  {name, size} into localStorage/Firestore. The real file bytes never
  reach the server, so nothing can ever "read" them.
- To fix that, the frontend needs to send each project file to a new
  endpoint (see the Flask snippet at the bottom of this file) the moment
  it's uploaded. That endpoint calls `extract_project_file_content` here,
  and returns the extracted text so the frontend can store it (e.g. in the
  Firestore project doc, alongside name/size) instead of throwing it away.
- Then, whenever the user is chatting inside a project, the frontend sends
  along the stored extracted text for every attached resource, and
  `build_project_context` turns that into a single string you prepend to
  the system prompt / user message for that turn.
"""

from Backend.file_reader import extract_text_from_file

# Keep per-file and total context sizes bounded so a big project doesn't
# blow out the prompt.
MAX_CHARS_PER_PROJECT_FILE = 8000
MAX_TOTAL_PROJECT_CONTEXT_CHARS = 24000


def extract_project_file_content(file_storage, max_chars=MAX_CHARS_PER_PROJECT_FILE):
    """
    Takes a single uploaded file (Flask FileStorage) and returns its
    extracted text, trimmed to max_chars. Returns None if the file type
    isn't supported or nothing could be extracted.
    """
    return extract_text_from_file(file_storage, max_chars=max_chars)


def build_project_context(project_name, project_description, resources,
                           max_total_chars=MAX_TOTAL_PROJECT_CONTEXT_CHARS):
    """
    Builds a single context string describing the project and its files,
    ready to be appended to the system prompt (or the user's message) for
    any chat happening inside that project.

    `resources` should be a list of dicts like:
        [{"name": "syllabus.pdf", "content": "...extracted text..."}, ...]
    where `content` may be None/empty if that file couldn't be read
    (e.g. an unsupported type) — those are still listed by name so the
    model knows the file exists, just not what's inside it.

    Returns "" if there's nothing to add (no project active).
    """
    if not project_name:
        return ""

    parts = [f"\n\n--- PROJECT CONTEXT ---"]
    parts.append(f"You are currently helping inside the project \"{project_name}\".")
    if project_description:
        parts.append(f"Project description: {project_description}")

    if not resources:
        parts.append("This project has no attached files yet.")
        return "\n".join(parts)

    parts.append(
        "The user has attached the following file(s) to this project. "
        "Use their contents below as background knowledge for this "
        "conversation, and reference them by name when relevant. If asked "
        "to make changes (e.g. rewrite, edit, continue, fix something in a "
        "file), base your answer on the actual content shown below rather "
        "than guessing.\n"
        "IMPORTANT: Whenever you output code or file content back to the "
        "user — whether the full file, a snippet, or an edited version — "
        "you MUST wrap it in a fenced code block using triple backticks "
        "with the correct language tag matching the file's extension "
        "(e.g. ```html for .html, ```python for .py, ```javascript for "
        ".js). Never paste code as plain unformatted paragraph text."
    )

    running_total = sum(len(p) for p in parts)
    for res in resources:
        name = res.get("name", "unknown file")
        content = (res.get("content") or "").strip()

        if not content:
            block = f"\n[File: {name}] (content not available — unsupported file type or read failed)"
        else:
            block = f"\n[File: {name}]\n{content}"

        if running_total + len(block) > max_total_chars:
            parts.append("\n[Additional project files were omitted to save space.]")
            break

        parts.append(block)
        running_total += len(block)

    parts.append("--- END PROJECT CONTEXT ---")
    return "\n".join(parts)


"""
=========================================================================
FLASK WIRING (reference only — add this to your app.py)
=========================================================================

1) New endpoint: extract text the moment a file is added to a project.
   projects.html's `handleFiles()` should POST each file here right after
   picking it, then store the returned `content` alongside {name, size}
   instead of throwing the file away.

    from Backend.project_files import extract_project_file_content

    @app.route('/api/project/extract-file', methods=['POST'])
    def extract_project_file():
        f = request.files.get('file')
        if not f:
            return jsonify({"error": "No file provided"}), 400
        content = extract_project_file_content(f)
        return jsonify({
            "name": f.filename,
            "content": content  # None if unsupported/failed — frontend should handle that
        })

2) Feed that stored content into the existing /api/chat endpoint whenever
   a project is active. Frontend (HomePage.html) already tracks
   `activeProject` with `.resources` — just also store `.content` on each
   resource (from step 1), then send the whole thing as JSON on every
   sendMessage() call:

    formData.append('project_name', activeProject ? activeProject.name : '');
    formData.append('project_description', activeProject ? activeProject.description : '');
    formData.append('project_resources', activeProject ? JSON.stringify(activeProject.resources) : '[]');

   Then in app.py's /api/chat handler:

    from Backend.project_files import build_project_context
    import json

    project_name = request.form.get('project_name', '')
    project_description = request.form.get('project_description', '')
    try:
        project_resources = json.loads(request.form.get('project_resources', '[]'))
    except ValueError:
        project_resources = []

    project_context = build_project_context(project_name, project_description, project_resources)

    # then append project_context to the system prompt or the user message
    # before calling get_ai_response / get_paid_ai_response / etc.
=========================================================================
"""