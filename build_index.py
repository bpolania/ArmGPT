#!/usr/bin/env python3
"""
build_index.py — Build a JSONL vector index from ARM documentation.

Reads .txt files from a docs directory, chunks them, embeds each chunk
via Ollama's /api/embed endpoint, and writes the result as JSONL.
"""

import os
import json
import glob
import argparse
from typing import List, Dict, Any

import requests

# Chunking config (simple word-based chunking)
MAX_WORDS_PER_CHUNK = 220
OVERLAP_WORDS = 40


def read_txt_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def chunk_text(text: str,
               max_words: int = MAX_WORDS_PER_CHUNK,
               overlap: int = OVERLAP_WORDS) -> List[str]:
    """Simple word-based chunking with overlap."""
    words = text.split()
    if not words:
        return []

    chunks = []
    step = max_words - overlap if max_words > overlap else max_words

    for i in range(0, len(words), step):
        chunk_words = words[i:i + max_words]
        chunk = " ".join(chunk_words).strip()
        if chunk:
            chunks.append(chunk)

    return chunks


def get_embedding(text: str, ollama_url: str, embed_model: str) -> List[float]:
    """Call Ollama /api/embed to get an embedding vector."""
    url = f"{ollama_url}/api/embed"
    payload = {
        "model": embed_model,
        "input": [text],
    }

    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Request to {url} failed: {e}")
        raise

    try:
        data = resp.json()
    except Exception as e:
        print(f"[ERROR] Failed to parse JSON from /api/embed response: {e}")
        print(f"Raw response text:\n{resp.text[:500]} ...")
        raise

    emb = None

    # Preferred: /api/embed format
    if isinstance(data, dict) and "embeddings" in data:
        embs = data.get("embeddings")
        if isinstance(embs, list) and len(embs) > 0 and isinstance(embs[0], list):
            emb = embs[0]

    # Fallback for /api/embeddings-like responses
    if emb is None and isinstance(data, dict) and "embedding" in data:
        possible = data.get("embedding")
        if isinstance(possible, list) and possible:
            emb = possible

    if not emb:
        print("[ERROR] Unexpected embedding response structure from Ollama:")
        print(json.dumps(data, indent=2)[:1000])
        raise RuntimeError("Failed to get a non-empty embedding vector from Ollama /api/embed")

    return emb


def build_index(docs_dir: str, output: str, ollama_url: str, embed_model: str) -> None:
    print(f"Scanning documents in {docs_dir} ...")
    txt_paths = sorted(glob.glob(os.path.join(docs_dir, "*.txt")))

    if not txt_paths:
        print("[WARN] No .txt files found in", docs_dir)
        return

    all_chunks: List[Dict[str, Any]] = []
    global_chunk_id = 0

    for path in txt_paths:
        fname = os.path.basename(path)
        print(f"  - Reading {fname}")
        raw_text = read_txt_file(path)
        doc_id = os.path.splitext(fname)[0]

        chunks = chunk_text(raw_text)
        for i, chunk_text_str in enumerate(chunks):
            all_chunks.append({
                "id": global_chunk_id,
                "doc_id": doc_id,
                "chunk_id": i,
                "source": fname,
                "text": chunk_text_str,
                "embedding": None,
            })
            global_chunk_id += 1

    print(f"Total chunks to embed: {len(all_chunks)}")
    if not all_chunks:
        print("[WARN] No chunks to embed; exiting.")
        return

    for idx, chunk in enumerate(all_chunks, start=1):
        txt = chunk["text"]
        print(f"[{idx}/{len(all_chunks)}] Embedding chunk id={chunk['id']} from {chunk['source']}")
        emb = get_embedding(txt, ollama_url, embed_model)
        chunk["embedding"] = emb

    num_missing = sum(1 for c in all_chunks if not c["embedding"])
    if num_missing > 0:
        print(f"[WARN] {num_missing} chunks ended up without embeddings.")

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            if chunk["embedding"] is None:
                chunk["embedding"] = []
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"[OK] Wrote {len(all_chunks)} chunks to {output}")
    embedded_count = sum(1 for c in all_chunks if c["embedding"])
    print(f"[OK] Chunks with non-empty embeddings: {embedded_count}")


def main():
    parser = argparse.ArgumentParser(
        description="Build a JSONL vector index from ARM documentation using Ollama embeddings"
    )
    parser.add_argument("--docs-dir", default="data/arm_docs",
                        help="Directory containing .txt source documents (default: data/arm_docs)")
    parser.add_argument("--output", default="data/arm_index.jsonl",
                        help="Output JSONL index path (default: data/arm_index.jsonl)")
    parser.add_argument("--embed-model", default="nomic-embed-text",
                        help="Ollama embedding model name (default: nomic-embed-text)")
    parser.add_argument("--ollama-url", default="http://localhost:11434",
                        help="Ollama API base URL (default: http://localhost:11434)")
    args = parser.parse_args()

    build_index(
        docs_dir=args.docs_dir,
        output=args.output,
        ollama_url=args.ollama_url,
        embed_model=args.embed_model,
    )


if __name__ == "__main__":
    main()
