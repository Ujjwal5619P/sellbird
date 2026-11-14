# Sellbird — Local AI Sales Agent

**EDXSO AI Engineer Intern Assignment 2**
**Local multi-product AI sales agent using Ollama**

Sellbird is an AI-assisted sales outreach platform. This assignment implementation adapts its AI inference layer to run locally using **Ollama and Qwen3:4B**, rather than relying on paid or cloud-hosted LLM inference.

The application supports multiple products, product-specific customer profiles, locally stored prospect research, and eight AI-assisted sales workflows. Generated content is stored locally and email drafts remain subject to human approval.

> **Assignment implementation:** This repository contains a local Ollama inference migration and local workflow implementation. It originated from the upstream Sellbird project. See the upstream repository and retain its applicable licensing and attribution.

## 1. Key features

- Local LLM inference through Ollama.
- Default local model: `qwen3:4b`.
- Multiple product profiles with product-specific ICP information.
- Local semantic embeddings using `all-MiniLM-L6-v2`.
- SQLite-backed local workflow and research storage.
- Hardware detection for RAM, CPU and GPU.
- No automatic fallback to Claude, Codex, OpenAI, Anthropic or another hosted LLM provider.
- Human approval before email sending.
- Offline workflow acceptance testing after required models and research data have been downloaded.

## 2. Technology stack

| Component | Technology |
|---|---|
| Application | Python |
| Dashboard | Existing Sellbird web dashboard |
| Backend | Existing Sellbird application and local workflow endpoints |
| Local LLM runtime | Ollama |
| LLM model | Qwen3:4B |
| Embeddings | Sentence Transformers |
| Embedding model | all-MiniLM-L6-v2 |
| Database | SQLite |
| Frontend | HTML, CSS and JavaScript |

## 3. Architecture

The local inference flow is:

1. The dashboard or acceptance test submits a workflow request.
2. The application loads the selected product and its saved context.
3. Local workflow logic prepares the prompt and relevant stored research.
4. The Ollama adapter sends the inference request to the local Ollama service.
5. Qwen3:4B generates the result on the local machine.
6. The application stores workflow results and history in SQLite.
7. The dashboard displays the generated result for review.

The embedding workflow loads its model from the local `models/all-MiniLM-L6-v2` directory and stores product-scoped embedding data in SQLite.

```text
Dashboard / Acceptance Test
            |
            v
      Local Workflow Layer
            |
       Product Context
       Saved Research
            |
            v
       Ollama Adapter
            |
            v
      Ollama — Qwen3:4B
            |
            v
      Generated Result
            |
            v
       SQLite Storage
            |
            v
        Dashboard
```

## 4. Eight AI sales workflows

The local workflow interface is available under **Products & research → Local AI sales workflows**.

| No. | Workflow | Purpose |
|---:|---|---|
| 1 | Business profile generation | Generates a business profile from stored company information. |
| 2 | ICP generation | Creates an Ideal Customer Profile for the selected product. |
| 3 | Prospect research | Analyses previously saved local prospect research. |
| 4 | Buying-signal classification | Identifies relevant buying signals from the supplied context. |
| 5 | Problem statement generation | Generates prospect-specific problem statements. |
| 6 | Personalised email generation | Drafts a personalised email using product and prospect context. |
| 7 | Prospect scoring | Evaluates prospect fit using the available context. |
| 8 | Reply classification | Classifies supplied sample conversation or reply text. |

All eight workflows were tested through the local acceptance script. The acceptance test reported **8 passed and 0 failed**, with `ollama` and `qwen3:4b` shown as the inference provider and model.

Email generation creates drafts; it does not mean an email was delivered.

## 5. Multi-product support

The Products & research dashboard supports creating and managing product profiles.

Each product can have its own:
- Product name and description.
- Pricing information.
- Key benefits.
- Product-specific ICP information.
- Saved research documents.
- Workflow context.

The workflow interface requires a product selection so the generated output can use the selected product's context.

## 6. Local research and semantic embeddings

The Local research library stores research text for later use.

Research can be collected during an online research step and saved locally. Subsequent prospect research workflows can use the saved documents without requiring a new web search.

The embedding implementation uses:
- Sentence Transformers.
- `all-MiniLM-L6-v2`.
- Local model loading.
- SQLite persistence.
- Product-scoped semantic retrieval.

See [LOCAL_EMBEDDINGS.md](LOCAL_EMBEDDINGS.md) for implementation and setup details.

## 7. Installation and setup — Windows

### Prerequisites

- Python installed.
- Git installed.
- Ollama installed.
- Sufficient RAM and storage for the selected local model.
- Internet access for initial installation and model downloads.

### Step 1 — Clone the repository

```cmd
git clone https://github.com/Ujjwal5619P/sellbird.git
cd sellbird
```

### Step 2 — Install the application

Use the repository's documented Python installation method and install the required dependencies.

```cmd
python -m pip install -e .
```

### Step 3 — Download and verify the Ollama model

```cmd
ollama pull qwen3:4b
ollama list
```

Make sure the model is available locally before running the application.

### Step 4 — Download the local embedding model

Follow the instructions in [LOCAL_EMBEDDINGS.md](LOCAL_EMBEDDINGS.md).

The embedding model must be downloaded before the offline test.

### Step 5 — Start the dashboard

```cmd
python -m sellbird dashboard
```

Open:

```text
http://127.0.0.1:5555
```

## 8. Running the acceptance tests

Start Ollama and ensure `qwen3:4b` is available.

Run the local workflow acceptance test:

```cmd
python sellbird_acceptance_test.py
```

Expected workflow names:

```text
business_profile
icp
prospect_research
buying_signals
problem_statement
personalized_email
prospect_score
reply_classification
```

Expected result:

```text
RESULT: 8/8 passed; 0/8 failed
No email delivery was invoked.
```

The acceptance script checks the workflow endpoints and reports the provider and model used.

### Offline acceptance test

After downloading the required model and embedding files and saving the research data:

1. Keep the local Ollama service running.
2. Keep the dashboard and required local services available.
3. Disconnect the machine from the internet.
4. Run the acceptance test again.

```cmd
python sellbird_acceptance_test.py
```

The offline test should use the locally available model and saved research. It must not silently fall back to a hosted LLM.

See `SUBMISSION_EVIDENCE/offline_acceptance_test.txt` and the screenshots in `SUBMISSION_EVIDENCE/Screenshots/` for recorded test evidence.

## 9. Hardware detection

The local workflow dashboard displays detected hardware and a suggested model.

The demonstration environment reported approximately:

| Resource | Detected information |
|---|---|
| RAM | 15.7 GB |
| CPU | Intel64 Family 6 Model 154 |
| GPU | NVIDIA GeForce RTX 2050 |
| GPU memory | 4096 MiB |
| Suggested model | qwen3:4b |

Model suitability depends on available memory, model quantization and the machine's runtime configuration.

## 10. Evidence and submission materials

The `SUBMISSION_EVIDENCE/` directory contains:

- `environment.txt` — environment information.
- `ollama_models.txt` — locally available Ollama models.
- `ollama_running.txt` — Ollama runtime evidence.
- `offline_acceptance_test.txt` — acceptance test output.
- `python_dependency_licenses.csv` — Python dependency license inventory.
- `Screenshots/` — dashboard and test screenshots.

The dependency CSV is an inventory, not a substitute for reviewing each dependency's license and obligations.

## 11. Local inference and security boundaries

The supported AI inference provider in this implementation is Ollama.

- Configuration validation restricts the supported inference provider to Ollama.
- The Brain entry point rejects unsupported inference providers.
- There is no automatic cloud inference fallback.
- The local embedding model is loaded from disk.
- Workflow and research data are stored locally in SQLite.
- Email drafts require human review; the acceptance test does not send emails.

**Important limitation:** This repository originated as a broader outreach platform and still contains legacy provider adapters and non-LLM integrations. The local inference changes do not establish that every external network integration or prospecting, enrichment, verification and email feature has been removed. Public research and other integrations may still involve network access. The offline acceptance test demonstrates the tested local workflows, not the removal of every network capability.

Do not commit `.env` files, API credentials, dashboard tokens, runtime databases, local model weights or personal backups.

## 12. Dependency and cost statement

The tested AI inference workflows use a locally running Ollama model. They do not require a paid hosted LLM API for inference.

Initial setup may require internet access to install dependencies and download model weights. External discovery or other integrations may have separate service requirements or costs; those are not represented as free local inference.

Review the dependency license inventory and the upstream project's license before redistribution.

## 13. Upstream project and license

This implementation is based on the upstream Sellbird project:

- Upstream repository: https://github.com/ethanplusai/sellbird
- License: see the repository's `LICENSE` and `NOTICE` files.

Retain the original copyright, attribution and applicable license notices when distributing modified source code.
