import os
import sys
import logging
from functools import lru_cache

# scikit-learn is optional for transformers, and its compiled files get blocked by
# Windows Smart App Control. Hide it so transformers doesn't try to import it.
sys.modules.setdefault("sklearn", None)

import torch
from dotenv import load_dotenv

from langchain.chains import RetrievalQA
from langchain_core.embeddings import Embeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from transformers import AutoModel, AutoTokenizer

load_dotenv()

logger = logging.getLogger(__name__)

DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

# Per-visitor state: session id -> {"chain": RetrievalQA, "history": [(q, a), ...]}
_sessions = {}


class MiniLMEmbeddings(Embeddings):
    """Sentence embeddings via transformers + torch (mean pooling, L2-normalized).

    Avoids the sentence-transformers package, which imports scikit-learn
    (its DLLs can be blocked by Windows Smart App Control).
    """

    def __init__(self, model_name, device):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(device).eval()

    def _embed(self, texts):
        vectors = []
        for i in range(0, len(texts), 32):
            batch = self.tokenizer(
                texts[i:i + 32], padding=True, truncation=True,
                max_length=256, return_tensors="pt",
            ).to(self.device)
            with torch.no_grad():
                hidden = self.model(**batch).last_hidden_state
            mask = batch["attention_mask"].unsqueeze(-1).float()
            pooled = (hidden * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
            pooled = torch.nn.functional.normalize(pooled, dim=1)
            vectors.extend(pooled.cpu().tolist())
        return vectors

    def embed_documents(self, texts):
        return self._embed(texts)

    def embed_query(self, text):
        return self._embed([text])[0]


@lru_cache(maxsize=1)
def _llm():
    return ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0.1,
        max_tokens=1024,
        reasoning_effort="low",
    )


@lru_cache(maxsize=1)
def _embeddings():
    return MiniLMEmbeddings("sentence-transformers/all-MiniLM-L6-v2", DEVICE)


def process_document(session_id, document_path):
    logger.info("Loading document: %s", document_path)
    documents = PyPDFLoader(document_path).load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    texts = splitter.split_documents(documents)
    logger.info("Split into %d chunks", len(texts))

    # One Chroma collection per visitor so uploads never mix between sessions.
    db = Chroma.from_documents(texts, embedding=_embeddings(), collection_name=f"s{session_id}")

    chain = RetrievalQA.from_chain_type(
        llm=_llm(),
        chain_type="stuff",
        retriever=db.as_retriever(search_type="mmr", search_kwargs={"k": 6, "lambda_mult": 0.25}),
        return_source_documents=False,
        input_key="question",
    )
    _sessions[session_id] = {"chain": chain, "history": []}


def process_prompt(session_id, prompt):
    state = _sessions.get(session_id)
    if state is None:
        return "Please upload a PDF first, then ask me about it."

    history = state["history"]
    if history:
        history_text = "\n".join(f"Q: {q}\nA: {a}" for q, a in history[-3:])
        full_prompt = f"Previous conversation:\n{history_text}\n\nNew question: {prompt}"
    else:
        full_prompt = prompt

    answer = state["chain"].invoke({"question": full_prompt})["result"]
    history.append((prompt, answer))
    return answer
