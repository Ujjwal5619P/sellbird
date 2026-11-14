"""Offline semantic search for locally saved Sellbird research documents.

Runtime is strictly local: SentenceTransformer is loaded from a filesystem path
with local_files_only=True. This module never downloads models or calls a remote API.
"""
from __future__ import annotations
import os, re, sqlite3, json
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable
import numpy as np
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL_DIR = Path(os.getenv("SELLBIRD_EMBEDDING_MODEL", "models/all-MiniLM-L6-v2"))
DEFAULT_DB = Path(os.getenv("SELLBIRD_EMBEDDING_DB", "data/local_embeddings.sqlite3"))

class LocalEmbeddingIndex:
    def __init__(self, model_dir: str | Path = DEFAULT_MODEL_DIR, db_path: str | Path = DEFAULT_DB):
        self.model_dir = Path(model_dir).expanduser().resolve()
        self.db_path = Path(db_path).expanduser().resolve()
        if not self.model_dir.is_dir():
            raise FileNotFoundError(
                f"Local embedding model not found: {self.model_dir}. "
                "Download it once with scripts/download_embedding_model.py; runtime will not use the network."
            )
        self.model = SentenceTransformer(str(self.model_dir), local_files_only=True, trust_remote_code=False)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS embedding_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                document_id TEXT NOT NULL,
                chunk_no INTEGER NOT NULL,
                text TEXT NOT NULL,
                vector BLOB NOT NULL,
                dimensions INTEGER NOT NULL,
                UNIQUE(product_id, document_id, chunk_no)
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_embedding_product ON embedding_chunks(product_id)")

    @contextmanager
    def _connect(self):
        """Yield a SQLite connection and always close its file handle.

        sqlite3.Connection's built-in context manager commits/rolls back but
        does not close the connection. Explicit closing is required on Windows
        before temporary database directories can be removed.
        """
        db = sqlite3.connect(str(self.db_path))
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def chunk_text(text: str, words: int = 350, overlap: int = 50) -> list[str]:
        tokens = re.findall(r"\S+", text or "")
        if not tokens:
            return []
        if words < 1 or overlap < 0 or overlap >= words:
            raise ValueError("Require words >= 1 and 0 <= overlap < words")
        step = words - overlap
        return [" ".join(tokens[i:i + words]) for i in range(0, len(tokens), step)]

    def add_document(self, product_id: str, document_id: str, text: str) -> int:
        if not product_id or not document_id:
            raise ValueError("product_id and document_id are required")
        chunks = self.chunk_text(text)
        if not chunks:
            return 0
        vectors = self.model.encode(chunks, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
        with self._connect() as db:
            db.execute("DELETE FROM embedding_chunks WHERE product_id=? AND document_id=?", (str(product_id), str(document_id)))
            db.executemany(
                "INSERT INTO embedding_chunks(product_id,document_id,chunk_no,text,vector,dimensions) VALUES(?,?,?,?,?,?)",
                [(str(product_id), str(document_id), i, chunk, np.asarray(vec, dtype=np.float32).tobytes(), int(len(vec)))
                 for i, (chunk, vec) in enumerate(zip(chunks, vectors))]
            )
        return len(chunks)

    def search(self, product_id: str, query: str, top_k: int = 5) -> list[dict]:
        if not product_id or not query.strip():
            return []
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        q = self.model.encode([query], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)[0]
        with self._connect() as db:
            rows = db.execute(
                "SELECT document_id, chunk_no, text, vector, dimensions FROM embedding_chunks WHERE product_id=?",
                (str(product_id),)
            ).fetchall()
        scored = []
        for doc_id, chunk_no, chunk, blob, dims in rows:
            vec = np.frombuffer(blob, dtype=np.float32, count=dims)
            if len(vec) == len(q):
                scored.append({"document_id": doc_id, "chunk_no": chunk_no, "text": chunk,
                               "score": float(np.dot(q, vec))})
        return sorted(scored, key=lambda x: x["score"], reverse=True)[:top_k]

    def count(self, product_id: str | None = None) -> int:
        with self._connect() as db:
            if product_id is None:
                return int(db.execute("SELECT COUNT(*) FROM embedding_chunks").fetchone()[0])
            return int(db.execute("SELECT COUNT(*) FROM embedding_chunks WHERE product_id=?", (str(product_id),)).fetchone()[0])
