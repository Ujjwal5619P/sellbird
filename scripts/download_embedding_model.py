"""One-time model download. Run while internet is available; inference stays local."""
from pathlib import Path
from sentence_transformers import SentenceTransformer

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
DEST = Path("models/all-MiniLM-L6-v2")
DEST.mkdir(parents=True, exist_ok=True)
print(f"Downloading {MODEL_ID} to {DEST} (one-time setup)...")
model = SentenceTransformer(MODEL_ID)
model.save(str(DEST))
print(f"Saved local model: {DEST.resolve()}")
print("Runtime uses this directory only; no remote model fallback is enabled.")
