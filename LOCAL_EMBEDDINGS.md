# Sellbird local semantic embeddings

## What this adds
- Sentence Transformers embeddings generated on the local machine.
- SQLite persistence in `data/local_embeddings.sqlite3` (separate from the main app DB to avoid changing existing migrations).
- Product-scoped similarity search; results are filtered by `product_id`.
- Strict local-only runtime: the model must exist on disk and is loaded with `local_files_only=True`.

## One-time setup (internet required only to obtain model files)
```cmd
pip install -r requirements-local-embeddings.txt
python scripts\download_embedding_model.py
```
Model: `sentence-transformers/all-MiniLM-L6-v2` (model card declares Apache-2.0; retain the model card and license in your submission bundle). Review the upstream model card before redistribution.

## Offline verification
Disconnect the internet after the model download, then run:
```cmd
python scripts\test_local_embeddings.py
```
Expected: local model load, two product-specific indexes, semantic search results, and PASS. The runtime module never downloads a model or uses an embedding API.

## Python usage
```python
from sellbird.local_embeddings import LocalEmbeddingIndex
index = LocalEmbeddingIndex()  # models/all-MiniLM-L6-v2, data/local_embeddings.sqlite3
index.add_document(product_id="product-id", document_id="research-doc-id", text="Previously downloaded research text")
hits = index.search(product_id="product-id", query="relevant prospect signal", top_k=5)
```

## Scope / honest status
This module is a working local embedding index and product-scoped semantic retrieval primitive. It is not yet wired into the dashboard's prospect-research endpoint; that integration is the next implementation step after the offline smoke test passes. No claim is made that existing prospect research already uses embeddings.
