import pdfplumber
import docx

MAX_CHARS_PER_FILE = 6000


def _extract_txt(file_storage):
    return file_storage.read().decode('utf-8', errors='ignore')


def _extract_csv(file_storage):
    return file_storage.read().decode('utf-8', errors='ignore')


def _extract_pdf(file_storage):
    text_parts = []
    with pdfplumber.open(file_storage) as pdf:
        for page in pdf.pages[:20]:  # cap at 20 pages
            text = page.extract_text()
            if text:
                text_parts.append(text)
    return '\n'.join(text_parts)


def _extract_docx(file_storage):
    doc = docx.Document(file_storage)
    return '\n'.join(p.text for p in doc.paragraphs)


EXTRACTORS = {
    'txt': _extract_txt,
    'csv': _extract_csv,
    'pdf': _extract_pdf,
    'docx': _extract_docx,
    'html': _extract_txt,
    'htm': _extract_txt,
    'md': _extract_txt,
    'json': _extract_txt,
    'py': _extract_txt,
    'js': _extract_txt,
}


def extract_text_from_file(file_storage, max_chars=MAX_CHARS_PER_FILE):
    """
    Takes a Flask FileStorage object, returns extracted text (trimmed to
    max_chars) or None if the file type isn't supported / extraction failed.
    """
    filename = file_storage.filename or ""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    extractor = EXTRACTORS.get(ext)
    if not extractor:
        return None

    try:
        text = extractor(file_storage)
        if not text:
            return None
        return text[:max_chars]
    except Exception as e:
        print(f"Failed to extract text from {filename}: {e}")
        return None


def build_file_context(uploaded_files, max_chars_per_file=MAX_CHARS_PER_FILE):
    """
    Takes a list of FileStorage objects (from request.files.getlist('files')),
    returns a single formatted string block to append to the user's message.
    Empty string if no files or nothing extractable.
    """
    context = ""
    for f in uploaded_files:
        if not f or not f.filename:
            continue
        text = extract_text_from_file(f, max_chars=max_chars_per_file)
        if text:
            context += f"\n\n--- Attached file: {f.filename} ---\n{text}"
        else:
            context += f"\n\n--- Attached file: {f.filename} (this file type can't be read as text) ---"
    return context