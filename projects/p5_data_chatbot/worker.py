"""PDF question answering without a vector database.

Serverless hosts keep no state between requests, so the browser holds the PDF's
text chunks and sends them with each question. Retrieval is BM25 (pure Python);
the answer comes from a Groq LLM.
"""
import math
import re
from collections import Counter

from pypdf import PdfReader

from groq_client import chat

CHUNK_CHARS = 1000
CHUNK_OVERLAP = 100
MAX_PAGES = 60
MAX_TOTAL_CHARS = 300_000
TOP_K = 6

_WORD = re.compile(r"\w+", re.UNICODE)


def extract_chunks(stream):
    """Read a PDF and return overlapping text chunks (list[str])."""
    reader = PdfReader(stream)
    text = "\n".join((page.extract_text() or "") for page in reader.pages[:MAX_PAGES])
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()[:MAX_TOTAL_CHARS]

    chunks, step = [], CHUNK_CHARS - CHUNK_OVERLAP
    for start in range(0, len(text), step):
        piece = text[start:start + CHUNK_CHARS].strip()
        if piece:
            chunks.append(piece)
    return chunks


def _tokens(text):
    return _WORD.findall(text.lower())


def retrieve(question, chunks, k=TOP_K):
    """Rank chunks against the question with BM25 and return the best k in document order."""
    docs = [_tokens(c) for c in chunks]
    n = len(docs)
    avg_len = (sum(len(d) for d in docs) / n) or 1
    df = Counter(t for d in docs for t in set(d))
    query = set(_tokens(question))

    def score(doc):
        tf, s = Counter(doc), 0.0
        for t in query:
            if t not in tf:
                continue
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            s += idf * tf[t] * 2.5 / (tf[t] + 1.5 * (0.25 + 0.75 * len(doc) / avg_len))
        return s

    ranked = sorted(range(n), key=lambda i: score(docs[i]), reverse=True)[:k]
    return [chunks[i] for i in sorted(ranked)]


def answer(question, chunks, history):
    context = "\n---\n".join(retrieve(question, chunks))
    system = (
        "Answer the user's question using only the document excerpts below. "
        "If the answer is not in the excerpts, say you don't know. Reply in the user's language.\n\n"
        f"Document excerpts:\n{context}"
    )
    turns = "\n".join(f"Q: {q}\nA: {a}" for q, a in history[-3:])
    prompt = f"Previous conversation:\n{turns}\n\nNew question: {question}" if turns else question
    return chat(system, prompt, max_tokens=1024)
