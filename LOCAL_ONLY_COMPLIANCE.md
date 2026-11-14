# Local-only inference and submission notes

## Inference policy

- The supported inference provider is **Ollama only** (`BRAIN_PROVIDERS = ("ollama",)`).
- The default provider is Ollama; the default model is selected by the Ollama adapter (`qwen3:4b`).
- Claude, Codex, OpenAI, Anthropic, and other hosted inference providers are rejected by configuration validation.
- The `Brain` constructor also fails closed if a non-Ollama provider is supplied directly.
- No automatic cloud fallback is permitted. If Ollama is unavailable, inference must report an error; deterministic/local application functions remain available.

## Local model and embeddings

- LLM runtime: Ollama, local HTTP endpoint `http://localhost:11434`.
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`, loaded from the local `models/all-MiniLM-L6-v2` directory with local-only loading.
- Embedding persistence: SQLite, product-scoped retrieval.
- Download model weights before the offline demonstration. Disconnect networking before running the offline acceptance test.

## Important remaining compliance boundary

This repository originated as a broader outreach platform and still contains legacy Claude/Codex adapter modules and non-LLM integrations. The configuration and `Brain` entry point now reject non-Ollama inference, but a complete submission audit must still review every legacy dashboard/CLI/provider route and every external prospecting, enrichment, verification, and email integration. Do not claim that all external network access has been removed. Public web research may be used only as an explicit online download step; offline workflows must consume saved local research.

## Privacy before publishing

Do not commit `.env` files, API credentials, `data/dashboard-token`, `data/agent-token`, SQLite runtime databases, model weights, or local backups. Rotate any token or credential that was included in an externally shared archive.

## Verification

Run the test suite and the eight-workflow acceptance script with Ollama running, then repeat the eight workflows after disconnecting internet access. Capture `ollama ps`, application status, and test output as evidence. Email sending must remain disabled during the demo.
