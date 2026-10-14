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

---

## Open decisions

| Topic             | To be decided in  | What we will compare                                                   |
| ----------------- | ----------------- | ---------------------------------------------------------------------- |
| Chunking strategy | Ingestion phase   | Fixed-size versus structure-aware chunks, measured on retrieval recall |
| Embedding model   | Retrieval phase   | Gemini embeddings versus an open model, on recall and cost             |
| Reranker          | Retrieval phase   | With and without a cross-encoder, on recall and latency                |
| Deployment target | Deployment phase  | Cloud Run versus AWS, on cost, setup effort and free-tier limits       |
| Cache design      | Reliability phase | Exact-match versus semantic cache, on hit rate and answer correctness  |
