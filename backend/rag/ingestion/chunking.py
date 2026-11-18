import re
import unicodedata

ZERO_WIDTH = "\u200b\u200c\u200d\u2060\ufeff"
KEEP_HYPHEN_PREFIXES = {
    "non", "sub", "self", "third", "anti", "co", "ex", "cross", "inter",
    "pre", "post", "semi", "quasi", "ultra", "counter", "multi", "re",
}
BULLET = "•"
MAX_TITLE_LINES = 2


# ---------------------------------------------------------------- cleaning
def clean_chars(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\xad", "")  # soft hyphen: join, don't split
    for ch in ZERO_WIDTH:  # zero-width chars are usually word separators
        text = text.replace(ch, " ")
    return "".join(
        c if c in "\n\t" or unicodedata.category(c)[0] != "C" else " "
        for c in text
    )


def strip_page_number(line: str, page_number: int) -> str:
    n = re.escape(str(page_number))
    if re.fullmatch(rf"\s*{BULLET}?\s*{n}\s*", line):  # number alone (or "• 32")
        return ""
    line = re.sub(rf"\s{{2,}}{n}\s*$", "", line)  # number at end of last line
    line = re.sub(rf"\s{{3,}}{n}\s{{2,}}", " ", line)  # number glued mid-line
    return line


def join_lines(parts: list) -> str:
    """Join wrapped lines; de-hyphenate only when it is safe."""
    out = ""
    for part in parts:
        if not out:
            out = part
            continue
        m = re.search(r"([A-Za-z]+)-$", out)
        if m and part[:1].islower():
            if m.group(1).lower() in KEEP_HYPHEN_PREFIXES:
                out += part
            else:
                out = out[:-1] + part
        else:
            out += " " + part
    return re.sub(r"[ \t]+", " ", out).strip()


# ---------------------------------------------------------------- parsing
def parse_slide(text: str, page_number: int):
    """Return (title, paragraphs) for one slide/page."""
    text = clean_chars(text)
    lines = []
    for line in text.split("\n"):
        line = strip_page_number(line.rstrip(), page_number)
        # bullet followed by a wide gap = layout artifact, not a list item
        line = re.sub(rf"^\s*{BULLET}\s{{6,}}", "", line)
        line = line.strip()
        if line == BULLET:
            line = ""
        lines.append(line)

    i = 0
    while i < len(lines) and not lines[i]:
        i += 1

    title_lines = []
    while (
        i < len(lines)
        and lines[i]
        and not lines[i].startswith(BULLET)
        and len(title_lines) < MAX_TITLE_LINES
    ):
        title_lines.append(lines[i])
        i += 1
    title = join_lines(title_lines)

    paragraphs, current = [], []

    def flush():
        if current:
            paragraphs.append(join_lines(current))
            current.clear()

    for line in lines[i:]:
        if not line:
            flush()
        elif line.startswith(BULLET):
            flush()
            current.append(line)
        else:
            current.append(line)
    flush()
    return title, [p for p in paragraphs if p]


# ---------------------------------------------------------------- sentences
# Tokens that end with a period but do not end a sentence in legal text.
ABBREVIATIONS = {
    "v", "vs", "art", "arts", "sec", "secs", "no", "nos", "j", "jj", "cj",
    "cji", "dr", "mr", "mrs", "ms", "hon", "ors", "anr", "etc", "viz", "ie",
    "eg", "cf", "para", "paras", "ch", "cl", "vol", "pp", "p", "regd", "retd",
    "s.c", "w.p", "cr.p.c", "i.p.c", "c.j.i", "a.i.r", "ltd", "co", "st", "dt",
    "i.e", "e.g",
}
_SENT_BOUNDARY = re.compile(
    r"(?:(?<=[.!?])|(?<=[.!?][\"”’')\]]))\s+(?=[\"“‘'(\[•]?[A-Z0-9])"
)


def _ends_with_abbreviation(fragment: str) -> bool:
    parts = fragment.split()
    if not parts:
        return False
    last = parts[-1]
    raw = last.strip("\"\u201c\u201d\u2018\u2019'()[],;:").rstrip(".")
    if raw.lower() in ABBREVIATIONS:
        return True
    # initials such as "K.S." / "D.Y." / "S." (capital letters separated by dots)
    return bool(re.fullmatch(r"(?:[A-Z]\.)*[A-Z]", raw)) and last.rstrip(")]\"\u201d\u2019'").endswith(".")


def split_sentences(text: str) -> list:
    pieces = _SENT_BOUNDARY.split(text.strip())
    sentences = []
    for piece in pieces:
        if sentences and _ends_with_abbreviation(sentences[-1]):
            sentences[-1] += " " + piece
        else:
            sentences.append(piece)
    return [s.strip() for s in sentences if s.strip()]


# ---------------------------------------------------------------- splitting
def split_words(text: str, chunk_size: int, overlap: int):
    """Last-resort splitter for a single sentence longer than chunk_size."""
    words = []
    for w in text.split():
        while len(w) > chunk_size:  # hard-split absurdly long tokens
            words.append(w[:chunk_size])
            w = w[chunk_size:]
        words.append(w)

    def length(ws):
        return len(" ".join(ws))

    chunks, current = [], []
    for word in words:
        if length(current + [word]) <= chunk_size:
            current.append(word)
            continue
        if current:
            chunks.append(" ".join(current))
        carry = []
        for w in reversed(current):
            if length([w] + carry) <= overlap:
                carry.insert(0, w)
            else:
                break
        while carry and length(carry + [word]) > chunk_size:
            carry.pop(0)
        current = carry + [word]
    if current:
        chunks.append(" ".join(current))
    return chunks


def split_large_paragraph(paragraph: str, chunk_size: int, overlap: int):
    """Pack whole sentences; overlap carries whole trailing sentences."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    chunks, current = [], []

    def length(ss):
        return len(" ".join(ss))

    for sentence in split_sentences(paragraph):
        if len(sentence) > chunk_size:  # one giant sentence: word fallback
            if current:
                chunks.append(" ".join(current))
                current = []
            chunks.extend(split_words(sentence, chunk_size, overlap))
            continue

        if length(current + [sentence]) <= chunk_size:
            current.append(sentence)
            continue

        chunks.append(" ".join(current))
        carry = []
        for s in reversed(current):
            if length([s] + carry) <= overlap:
                carry.insert(0, s)
            else:
                break
        while carry and length(carry + [sentence]) > chunk_size:
            carry.pop(0)
        current = carry + [sentence]

    if current:
        chunks.append(" ".join(current))
    return chunks


# ---------------------------------------------------------------- chunking
CASE_MARKER = re.compile(r"\b[Vv]s?\.?\s")


def _is_context_line(paragraph: str) -> bool:
    """Short non-bullet line before the bullets, e.g. a case citation."""
    if paragraph.startswith(BULLET) or len(paragraph) > 160:
        return False
    return bool(CASE_MARKER.search(paragraph)) or not paragraph.rstrip().endswith(
        (".", "\u201d", '"')
    )


def chunk_slide(text: str, chunk_size: int, overlap: int, page_number: int):
    """
    Chunks for one page. Every chunk starts with the slide title plus any
    short lead-in line (usually the case citation), so no chunk loses
    the case it is about.
    """
    title, paragraphs = parse_slide(text, page_number)

    lead = []
    while (
        paragraphs
        and len(lead) < 2
        and _is_context_line(paragraphs[0])
        and any(p.startswith(BULLET) for p in paragraphs[1:])
    ):
        lead.append(paragraphs.pop(0))

    header = "\n".join(x for x in [title, *lead] if x)
    prefix = f"{header}\n\n" if header else ""
    budget = max(chunk_size - len(prefix), chunk_size // 2)

    bodies, current = [], ""
    for p in paragraphs:
        if len(p) > budget:
            if current:
                bodies.append(current)
                current = ""
            bodies.extend(split_large_paragraph(p, budget, min(overlap, budget - 1)))
            continue
        candidate = f"{current}\n\n{p}" if current else p
        if len(candidate) <= budget:
            current = candidate
        else:
            bodies.append(current)
            current = p
    if current:
        bodies.append(current)

    context_line = " ".join(lead) or None
    if not bodies and header:  # title-only slide
        return [{"text": header, "title": title, "context_line": context_line}]
    return [{"text": prefix + b, "title": title, "context_line": context_line} for b in bodies]


def chunk_pages(
    pages: list,
    chunk_size: int,
    overlap: int,
    source: str,
    document_title: str = "",
    case_names: dict = None,
):
    """
    text            -> exact document text (slide title + body). Use for the LLM
                       context and for citations.
    retrieval_text  -> text plus context. Use ONLY for embedding and reranking.
    chunk_key       -> stable id (page + index) so relevance labels survive
                       re-chunking; chunk_id is a global counter and will shift.
    case_names      -> optional hand-curated {page_number: "A v. B"} map.
    """
    case_names = case_names or {}
    all_chunks, counter = [], 1
    for page in pages:
        page_number = page["page_number"]
        case_name = case_names.get(page_number)
        slide_chunks = chunk_slide(page["text"], chunk_size, overlap, page_number)
        for idx, c in enumerate(slide_chunks, start=1):
            context = []
            if document_title:
                context.append(f"Document: {document_title}")
            if case_name:
                context.append(f"Case: {case_name}")
            retrieval_text = ("\n".join(context) + "\n\n" + c["text"]) if context else c["text"]

            all_chunks.append({
                "chunk_id": f"chunk_{counter:05d}",
                "text": c["text"],
                "retrieval_text": retrieval_text,
                "metadata": {
                    "source": source,
                    "document_title": document_title or None,
                    "page_number": page_number,
                    "section_title": c["title"] or None,
                    "case_name": case_name,
                    "context_line": c["context_line"],
                    "chunk_key": f"p{page_number:03d}_c{idx:02d}",
                },
            })
            counter += 1
    return all_chunks