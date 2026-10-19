# Niyam decision log

One entry per significant decision: what we chose, what else we considered, why, and what it costs us. Newest decisions go at the bottom. Status is one of: accepted, superseded, open.

Format of each entry: context, options considered, decision, trade-off.

---

## D-001: Modular monolith plus one background worker

- **Date:** 2026-10-13. **Status:** accepted.
- **Context:** Solo project that needs production practices but not independent scaling of many services.
- **Options:** (a) microservices, (b) single process with no worker, (c) modular monolith with one worker for ingestion.
- **Decision:** (c). One FastAPI application with strict package boundaries, plus a separate worker process for document ingestion.
- **Why:** Ingestion is slow and bursty, so it must not run inside request handling. Everything else has no reason to be a separate deployable. Microservices add network failures, deployment overhead and debugging cost without a benefit at this size.
- **Trade-off:** One deployable unit means one failure domain. Clean package boundaries keep a later split possible.

## D-002: PostgreSQL with pgvector, not a separate vector database

- **Date:** 2026-10-13. **Status:** accepted.
- **Options:** Postgres with pgvector, Qdrant, Chroma, Pinecone.
- **Decision:** Postgres with pgvector, plus Postgres full-text search.
- **Why:** One datastore holds relational data, vectors and keyword search. Hybrid retrieval then runs against one system with transactional consistency, one backup story and one thing to deploy. Our corpus (thousands to tens of thousands of chunks) is far below the scale where a dedicated vector database pays off.
- **Trade-off:** Fewer specialised vector features and less headroom at very large scale. Revisit if the corpus grows by orders of magnitude.

## D-003: Models are selected by configuration only

- **Date:** 2026-10-13. **Status:** accepted.
- **Context:** Model names, providers and prices change quickly.
- **Decision:** Gemini is the default for generation and embeddings. Provider and model names come from environment variables through one settings object and one factory function. No other module names a model.
- **Why:** Switching models is a configuration change, which limits vendor lock-in and allows a fallback model.
- **Trade-off:** Changing the embedding model requires re-indexing, because vectors from different models are not compatible. The index stores the embedding model name and dimension, and the app refuses to start if they disagree with the configuration. Prompts can behave differently across models, so any model change must pass the evaluation suite before it is accepted.

## D-004: LangChain for integrations, LangGraph for orchestration, with boundaries

- **Date:** 2026-10-13. **Status:** accepted.
- **Options:** raw provider SDKs only, LangChain only, LangChain plus LangGraph, a different agent framework.
- **Decision:** LangChain for model, prompt, structured-output, text-splitter and tool abstractions. LangGraph for the stateful question-answering graph. LangChain types are confined to the llm, retrieval and agents packages. The API, database and evaluation layers use our own Pydantic models.
- **Why:** The frameworks remove boilerplate and give tracing, retries and fallbacks. The boundary keeps tests framework-independent and limits the blast radius of API changes.
- **Trade-off:** An extra layer of abstraction to learn and debug. We accept it because it is widely used, and we keep control of the parts that matter most.

## D-005: Hybrid retrieval is hand-written

- **Date:** 2026-10-13. **Status:** accepted.
- **Options:** vector search only, keyword search only, a framework's built-in hybrid retriever, hand-written hybrid.
- **Decision:** Run Postgres full-text and pgvector searches separately, merge with reciprocal rank fusion, then rerank with a cross-encoder.
- **Why:** Regulations contain exact terms (section numbers, defined terms) that vector search handles poorly, and paraphrased questions that keyword search misses. Doing the fusion ourselves makes each step measurable and explainable.
- **Trade-off:** More code to maintain. Evaluation (D-011) will tell us whether each stage is earning its place.

## D-006: LangSmith for LLM tracing, OpenTelemetry for the service

- **Date:** 2026-10-13. **Status:** accepted. Supersedes an earlier plan to use Langfuse.
- **Decision:** LangSmith for traces of chains, retrieval, tool and model calls and for experiment comparison. OpenTelemetry and structured JSON logs for the API and database layers.
- **Why:** LangSmith is native to LangChain and LangGraph, so tracing needs almost no code. Running two LLM-tracing tools would duplicate effort.
- **Trade-off:** LangSmith is hosted, so prompts and answers leave our infrastructure. Documents are public, and personal data in user questions will be redacted before anything is traced. Free-tier limits will be checked when we reach the observability phase.

## D-007: Streamlit for the frontend

- **Date:** 2026-10-13. **Status:** accepted.
- **Options:** Streamlit, React or Next.js.
- **Decision:** Streamlit, calling the FastAPI service over HTTP and holding no business logic.
- **Why:** The project's value is in the backend and the AI layer. A second toolchain would cost time better spent on evaluation, security and deployment.
- **Trade-off:** Less control over UI polish. Because the UI is a thin client, replacing it later does not touch the backend.

## D-008: Tooling baseline: uv, src layout, ruff, strict mypy, pytest

- **Date:** 2026-10-13. **Status:** accepted.
- **Decision:** uv for environments and a committed lockfile, a src layout, ruff for linting and formatting, mypy in strict mode, pytest for tests. Development tools live in a separate dependency group.
- **Why:** Reproducible installs, tests that run against the installed package, and strict typing from the first line, which is much cheaper than retrofitting it. A separate dev group keeps the production image small.

## D-009: Configuration from environment variables, validated at startup

- **Date:** 2026-10-14. **Status:** accepted.
- **Decision:** pydantic-settings with a NIYAM_ prefix, values read from the environment or a local .env file, restricted values expressed as Literal types. The .env file is ignored by git, and a .env.example with fake values will be committed.
- **Why:** Secrets never enter the repository, and an invalid value stops the application at startup with a clear error instead of failing later at runtime.

## D-010: LF line endings enforced through .gitattributes

- **Date:** 2026-10-13. **Status:** accepted.
- **Context:** Development happens on Windows, deployment happens in Linux containers.
- **Decision:** A .gitattributes rule forces LF line endings for text files.
- **Why:** CRLF line endings in shell scripts or Dockerfiles can break Linux builds in ways that are hard to spot.

## D-011: Build the evaluation set before the generator

- **Date:** 2026-10-13. **Status:** accepted.
- **Decision:** The labelled question set and retrieval metrics (recall@k, MRR) are built before answer generation, and every later change is judged against them. Evaluation runs in CI as a quality gate.
- **Why:** Without a baseline, "improvement" is an opinion. This ordering also lets us show which retrieval stages (keyword, vector, fusion, reranking) actually help.

## D-012: Arq for background jobs

- **Date:** 2026-10-13. **Status:** accepted.
- **Options:** Celery, RQ, Arq, FastAPI background tasks.
- **Decision:** Arq, using the Redis instance we already need for caching and rate limiting.
- **Why:** Async-native, small, and a good match for an async application. FastAPI background tasks die with the process, and Celery is heavier than a single worker needs.
- **Trade-off:** A smaller ecosystem than Celery.

## D-013: No default model names in code; API key as a secret value

- **Date:** 2026-10-14. **Status:** accepted. Refines D-003.
- **Context:** Provider docs and model names change often. LangChain's documentation example used a Gemini model name that did not appear on Google's current model list.
- **Options:** (a) default model names in code, (b) default model names in the settings class, (c) no defaults, names supplied through configuration.
- **Decision:** (c). Provider, model and embedding model settings are optional in the settings class and empty by default. The model factory stops with a clear message if a model name is missing. The API key is a `SecretStr` and is read from a git-ignored `.env`. A `.env.example` with fake values is committed as the template.
- **Why:** A default is a hidden hard-coded model name, which brings back the problem D-003 set out to avoid. Treating the key as a secret value keeps it out of logs.
- **Trade-off:** A missing model name is found when the model is first requested, not at application startup. We will add a startup check when the API is built.

## D-014: Thin model factory over LangChain (supersedes LiteLLM)

**Context.** The model must be changeable by configuration only, and we already use LangChain.
**Decision.** One function, `build_chat_model(settings)`, wraps `init_chat_model`. Model name and provider come from `Settings`. Only `niyam.llm` builds models or reads the API key.
**Why.** LangChain already abstracts providers, so a second abstraction layer (LiteLLM) would duplicate it. A thin factory keeps one seam and no extra dependency.
**Consequences.** Swapping a model is an environment change. A wrong model name fails on first call, not at build time, so a startup check will be added later.

## D-015: Local pre-commit hooks that call project tools through uv

**Context.** A failed format check was committed and pushed, and only CI caught it.
**Decision.** Use pre-commit with `repo: local` hooks that run `uv run ruff`, `uv run mypy` and `uv run pytest`. Ruff runs at commit time. Mypy and pytest run at push time.
**Why.** Local hooks use the tool versions in `uv.lock`, so hooks, local runs and CI cannot disagree. Splitting by stage keeps commits fast while slow checks still run before code leaves the machine.
**Consequences.** Hooks live in `.git/hooks`, so each clone must run the install command once. `--no-verify` can skip them, so CI stays the final gate.

## D-016: Single-stage Docker image with uv, non-root user and health check

**Context.** The app must run identically on a laptop, in CI and in the cloud.
**Decision.** Build from `python:3.12-slim`, copy a pinned uv binary, install locked runtime dependencies in a separate layer before copying code, run as a non-root user, and add a `HEALTHCHECK` on `/health`. `.dockerignore` excludes `.env`, `.git`, `.venv`, tests and docs.
**Why.** Layer order gives fast rebuilds. `--locked --no-dev` keeps the image reproducible and small. Non-root limits the damage of a compromise. Excluding `.env` means secrets cannot be baked into image layers.
**Trade-offs.** Single-stage is simpler to read than multi-stage but slightly larger (517 MB unpacked, 117 MB compressed). Revisit if size or start time matters.

## D-017: PostgreSQL 16 + pgvector via Docker Compose

- **Status:** Accepted
- **Context:** Niyam needs one store for documents, chunks, vectors and full-text search. Developers need an identical database on every machine and in CI.
- **Decision:** Run `pgvector/pgvector:0.8.0-pg16` through `compose.yaml`. The image tag is pinned to an exact version. Credentials and the host port come from `.env` and fail fast if missing (`${VAR:?msg}`). The port is published on `127.0.0.1` only. Data lives in the named volume `niyam_pgdata`.
- **Why:** One database for relational data, vectors and keyword search keeps the system simple, and hybrid retrieval can run in a single SQL query. Pinning avoids surprise upgrades. Binding to localhost keeps the database off the network.
- **Consequences:** The host port is configurable (`NIYAM_DB_PORT`) because 5432 was already taken by a local Postgres on one machine. The container port stays 5432.

## D-018: Database access layer, timeouts and readiness endpoint

- **Status:** Accepted
- **Context:** The API needs a database connection that is safe with secrets, never hangs, and reports its state to orchestrators and monitoring.
- **Decision:** `Settings` holds `NIYAM_DB_*` values (password as `SecretStr`). `db/engine.py` builds the URL with SQLAlchemy `URL.create`, creates the engine with `pool_pre_ping` and a 5-second connect timeout, and exposes `check_database()` which returns a bool and logs failures. The API exposes `/health` (liveness, no dependencies) and `/ready` (readiness, 200 or 503 depending on the database). The database check is injected into `create_app`, and the real engine is created lazily on first use.
- **Why:** `URL.create` escapes special characters in passwords. The secret is unwrapped in exactly one place. A missing timeout turned a stalled Docker port forwarder into a frozen process, so every network call gets a bounded wait. Keeping liveness independent of the database prevents restart storms during a database outage. Injection keeps API tests free of Docker.
- **Consequences:** The app starts without a database or password (readiness reports not ready). Worst-case check time is about 10 seconds because psycopg tries both IPv6 and IPv4 addresses; to be tuned when probes are configured.

## D-019: Schema, pgvector sizing and migrations

- **Status:** Accepted
- **Context:** Niyam needs to store circular metadata, text chunks, vectors and keyword-search data in one place, with a schema that can be rebuilt identically anywhere.
- **Decision:** Two tables. `documents` holds one row per circular (regulator, circular number, title, issue date, status, source URL, content hash). `chunks` holds one row per passage (position, page, section, text, embedding, embedding model, generated full-text column). Embeddings are `vector(768)` with an HNSW cosine index. Keyword search uses a generated `tsvector` column with a GIN index. `regulator` and `status` are enforced by `CHECK` constraints. Constraint names follow a naming convention. The schema is created only through Alembic migrations, and the first migration also enables the `vector` extension.
- **Why:** 768 dimensions fit under pgvector's 2000-dimension limit for HNSW indexes while keeping storage and search fast. A nullable embedding lets ingestion work in stages. Storing the embedding model name per chunk prevents mixing vectors from different models. A generated column means the keyword index can never go stale. Database-level checks protect integrity from any writer. Migrations make the schema reviewable, repeatable and reversible.
- **Deferred on purpose:** a `supersedes` link between circulars and a unique constraint on circular number, until real data shows how they are numbered and amended.
- **Consequences:** Changing the embedding size needs a new migration and a full re-embed. Downgrading does not drop the `vector` extension.

## D-020: Document parsing with Docling

- **Status:** Accepted
- **Context:** Niyam must turn RBI and SEBI circular PDFs into clean text and tables with reliable page numbers. Regulatory answers often depend on tables (for example, minimum investment limits per fund category), so table quality decides answer quality.
- **Options tested:** PyMuPDF (fast, light) and Docling (layout and table models), run on the same hard pages from three real documents.
- **Decision:** Use Docling as the parsing engine, behind a small parser interface so it can be replaced. Ingestion runs as a background job, not in the API process, and its heavy dependencies live in an optional dependency group so the API image stays small.
- **Why:** On a real SEBI scheme-categorisation table, PyMuPDF produced 21 jumbled columns with every cell repeated, while Docling produced a clean four-column table with one row per scheme. All three PDFs have a text layer, so no OCR is needed. LangChain loaders do not change this, because they wrap an engine and the engine decides the quality.
- **Known limitations:** Docling assigned the last line of one table cell to the next row (a "- 25% of total assets" line moved from the Multi Cap row to the Large Cap row). This becomes a case in the evaluation set (Phase 5). The "Withdrawn" watermark on withdrawn RBI documents is part of the text layer and appears between sentences, once per page, so ingestion removes it at the document-structure level and uses it as a cross-check against the manifest status. Parsing takes roughly 5 to 10 seconds per page on CPU.
- **Page numbers:** Citations use the physical page number counted from 1, as shown by a PDF viewer. The PDFs carry no page-label metadata and the printed numbers differ (SEBI annexures have no footer numbers).
- **Consequences:** Large install (PyTorch). Models must be downloaded at build time, never at runtime, and the container must be tested with no network. Ingestion is slow, so it runs as a background job.

## D-021: Code graph for architecture review, refreshed after each commit

- **Status:** Accepted
- **Context:** As the codebase grows, it helps to see how modules and layers connect, and to catch dependencies that cut across layers. The graph must always match the code, or people stop trusting it.
- **Options considered:** (1) run Graphify by hand when needed, (2) Graphify's own `hook install`, (3) a hook declared in `.pre-commit-config.yaml`, (4) a CI job that publishes the graph.
- **Decision:** Use Graphify in code-only mode (`graphify update . --force`), run as a post-commit hook declared in `.pre-commit-config.yaml`. `.graphifyignore` limits the graph to application code: tests, migrations, scratch files, data, docs, README and `pyproject.toml` are excluded. The output folder `graphify-out/` is generated and git-ignored. The viewer, `tools/graphify-explorer.html`, is committed because it is hand-written source, and it loads `graphify-out/graph.json` in the browser.
- **Why:** The hook runs after the commit is saved, so it can never block a commit. It takes about 2 seconds and needs no API key, because AST extraction is local. Keeping it in the pre-commit config puts every git hook in one reviewed, versioned file, whereas Graphify's own installer writes four hooks directly into `.git/hooks`, where nobody can review them and they can conflict with the pre-commit framework. Option 4 was rejected for now because the graph is a development aid, not a delivery artifact.
- **Found while testing:** `graphify update` also indexes documentation (86 nodes from `docs/` and 10 from the README) where `extract --code-only` does not. These nodes drowned the code structure, so docs are excluded in `.graphifyignore`. The command leaves the graph untouched when no code topology changed, so a passing hook does not always mean a rewrite. The hook was verified by adding a throwaway function and watching the node count go from 61 to 62.
- **Upgrades:** The tool is installed with `uv tool` and is upgraded on purpose with `uv tool upgrade graphifyy`, then the graph is rebuilt and its node count compared. It is not upgraded automatically, because a new version can change the output format and silently break the viewer.
- **Consequences:** Each developer must install the post-commit hook once with `pre-commit install --hook-type post-commit`. The graph is local only and is not available in CI. Community names stay as "Community N", because naming them needs an LLM key and we run without one.

## D-022: Structure-aware chunking, with LangChain at the boundaries

- **Status:** Accepted for version 1. The comparison with a fixed-size baseline is scheduled for Phase 5.
- **Context:** Chunks are what we embed, retrieve and cite. Regulatory answers often sit inside tables, and every answer must cite the physical page it came from.
- **Options:** (1) LangChain's `RecursiveCharacterTextSplitter` (size-based, works on plain strings), (2) Docling's own table-aware chunker, (3) our own chunker over parsed blocks.
- **Decision:** Write a small chunker over `ParsedBlock` objects (`chunk_blocks`). A heading starts a new section. Text blocks are grouped up to a size limit, never cut in half. A table is always its own chunk. Each chunk carries the page where it starts and its section heading. The heading is stored in `section` and not repeated in `text`.
- **Why:** String-based splitters cannot see the two rules the product depends on: never split a table, and keep the physical page for the citation. The chunker is about 50 lines and covered by six tests that read as a specification.
- **LangChain's role:** `RecursiveCharacterTextSplitter` is the fixed-size baseline in the Phase 5 evaluation, and it will split any single paragraph that is larger than the size limit. Chunks become LangChain `Document` objects (text plus page and section metadata) when they leave ingestion, so embeddings, retrieval, the chat model, LangGraph and LangSmith all use LangChain's interfaces.
- **Known limitations:** The 1200-character limit is a starting guess, not a measured value. A single paragraph over the limit currently stays whole. Table rows are not repeated with their header when a long table is split, because tables are never split at all.
- **Consequences:** If the evaluation shows the baseline retrieves as well or better, we switch to it, because the chunker sits behind a single function.

---

## Open decisions

| Topic             | To be decided in  | What we will compare                                                   |
| ----------------- | ----------------- | ---------------------------------------------------------------------- |
| Chunking strategy | Ingestion phase   | Fixed-size versus structure-aware chunks, measured on retrieval recall |
| Embedding model   | Retrieval phase   | Gemini embeddings versus an open model, on recall and cost             |
| Reranker          | Retrieval phase   | With and without a cross-encoder, on recall and latency                |
| Deployment target | Deployment phase  | Cloud Run versus AWS, on cost, setup effort and free-tier limits       |
| Cache design      | Reliability phase | Exact-match versus semantic cache, on hit rate and answer correctness  |
