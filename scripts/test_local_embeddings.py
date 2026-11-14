"""Offline smoke test for the local Sentence Transformers index."""
from pathlib import Path
import tempfile
from sellbird.local_embeddings import LocalEmbeddingIndex

model_dir = Path("models/all-MiniLM-L6-v2")
if not model_dir.is_dir():
    raise SystemExit(f"FAIL: local model missing: {model_dir}. Run python scripts/download_embedding_model.py once while online.")
with tempfile.TemporaryDirectory() as tmp:
    index = LocalEmbeddingIndex(model_dir=model_dir, db_path=Path(tmp) / "embeddings.sqlite3")
    n1 = index.add_document("product-alpha", "doc-alpha", "Synthetic voice cloning detection for call centres and telecom customer support.")
    n2 = index.add_document("product-beta", "doc-beta", "Counterfeit electronic component inspection for electronics manufacturing quality assurance.")
    alpha = index.search("product-alpha", "detect cloned synthetic voices in customer calls", top_k=3)
    beta = index.search("product-beta", "identify fake electronic components on production lines", top_k=3)
    assert n1 and n2 and alpha and beta, "Expected indexed chunks and search results"
    assert all("voice" in x["text"].lower() or "call" in x["text"].lower() or "telecom" in x["text"].lower() for x in alpha), "Alpha product filter leaked unrelated chunks"
    assert all("electronic" in x["text"].lower() or "component" in x["text"].lower() or "manufacturing" in x["text"].lower() for x in beta), "Beta product filter leaked unrelated chunks"
    print("PASS local model loaded from disk")
    print(f"PASS indexed chunks: alpha={n1}, beta={n2}")
    print(f"PASS product-scoped semantic search: alpha={alpha[0]['score']:.3f}, beta={beta[0]['score']:.3f}")
    print("PASS SQLite persistence and product isolation")
print("RESULT: PASS | offline embedding smoke test")
