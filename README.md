# Niyam

[![CI](https://github.com/Musharraf-Bubere/niyam/actions/workflows/ci.yml/badge.svg)](https://github.com/Musharraf-Bubere/niyam/actions/workflows/ci.yml)

Grounded question answering over RBI and SEBI regulations. Ask a question about a circular, get an answer with citations to the source text, or a refusal when the evidence is weak.

> **Status: under active development (Phase 1, foundation).** The features below are the plan, not all built yet. The status table shows what exists today.

## Why this project

Regulatory text is long, dense and changes often. A plain chatbot can sound confident and be wrong. Niyam is designed around the opposite rule: every answer must point to the exact passage it came from, and when the retrieved evidence is weak the system says so instead of guessing.

## Status

| Area                                                 | State   |
| ---------------------------------------------------- | ------- |
| Project setup, tooling, CI                           | Done    |
| Configuration and logging                            | Done    |
| Chat model factory (model changeable by config only) | Done    |
| Data layer (PostgreSQL, pgvector)                    | Done    |
| Ingestion of RBI and SEBI circulars                  | Planned |
| Hybrid retrieval and reranking                       | Planned |
| Evaluation harness                                   | Planned |
| Answer generation with citations                     | Planned |
| API (FastAPI) and Streamlit UI                       | Planned |
| Agent orchestration (LangGraph)                      | Planned |
| Guardrails, observability (LangSmith), deployment    | Planned |

## Tech choices

Python 3.12, uv, LangChain with Gemini, Pydantic settings, structlog, ruff, mypy (strict), pytest, GitHub Actions. Planned: FastAPI, PostgreSQL with pgvector, LangGraph, Streamlit, Docker, LangSmith.

The reasoning behind each choice is recorded in [docs/decision-log.md](docs/decision-log.md).

## Documentation

- [Problem and solution](docs/01-problem-and-solution.md)
- [Architecture](docs/02-architecture.md)
- [Decision log](docs/decision-log.md)

## Getting started

Requirements: Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/Musharraf-Bubere/niyam.git
cd niyam
uv sync
```

Install the Git hooks once, so checks run automatically before each commit and push:

```bash
uv run pre-commit install --hook-type pre-commit --hook-type pre-push
```

Create your local settings file from the example and add your own values. The real `.env` is git-ignored and must never be committed.

```bash
cp .env.example .env
```

On Windows PowerShell use `Copy-Item .env.example .env`.

To use a different model, change `NIYAM_LLM_MODEL` in `.env`. No code changes are needed.

## Quality checks

The same checks run locally and in CI on every push:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

Unit tests use a fake model, so they need no API key and no network.

## Developer tools

Niyam keeps an up-to-date map of its own code, so layers and dependencies are easy to review.

- **Enable the automatic refresh once:** `uv run pre-commit install --hook-type post-commit`. After every commit, the code graph is rebuilt in about 2 seconds, with no API key and no network.
- **Explore the graph:** open `tools/graphify-explorer.html` in a browser (it needs internet for its CDN libraries) and load `graphify-out/graph.json`. You can search, filter by community, inspect a node and trace the shortest path between two nodes.
- **Rebuild by hand:** `graphify update . --force`.
- **Upgrade the tool on purpose:** `uv tool upgrade graphifyy`, then rebuild and compare the node count, because a new version can change the output format.
- **Scope:** `.graphifyignore` limits the graph to application code. `graphify-out/` is generated and git-ignored.

Why it works this way: see [D-021](docs/decision-log.md).

## Run with Docker

```bash
docker build -t niyam:dev .
docker run -d --name niyam -p 127.0.0.1:8000:8000 niyam:dev
```

Then open http://127.0.0.1:8000/health. The image contains only the application code and runtime dependencies. Secrets are never baked in; they are passed as environment variables when the container starts.

## Project layout

```text
src/niyam/
  core/   configuration and logging
  llm/    chat model factory
tests/
docs/
```

More packages (db, ingestion, retrieval, agents, api) arrive in later phases, following the layering rules in the architecture document.
