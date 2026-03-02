"""
RAG fixture: shows how indexing might be wired.
No real indexing happens unless ENABLE_INDEXING=1.
"""

import os

ENABLE_INDEXING = os.getenv("ENABLE_INDEXING", "0") == "1"

SENSITIVE_MARKERS = [
    "ssn", "passport", "credit card", "medical history",
    "iban", "routing number", "account number"
]

def index_documents(paths: list[str]) -> dict:
    # Pattern scanners like: data flow from docs -> embeddings -> vector store
    if not ENABLE_INDEXING:
        return {"status": "skipped", "reason": "ENABLE_INDEXING=0"}

    # Placeholder: in a real app you'd load docs, chunk, embed, store.
    return {"status": "indexed", "count": len(paths), "notes": "fixture-only"}

def retrieve(query: str) -> dict:
    # Retrieval without tenant isolation / filtering (fixture evidence)
    return {"query": query, "top_k": 10, "chunks": ["[chunk1]", "[chunk2]"]}

def answer(query: str) -> str:
    ctx = retrieve(query)
    # Risky pattern: returning raw chunks
    return f"Q: {query}\nCTX: {ctx['chunks']}\nA: (model output here)"