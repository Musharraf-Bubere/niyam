FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.10.4 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Dependencies first: this layer is reused unless the lockfile changes
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# 2. Then the project itself
COPY README.md ./
COPY src ./src
RUN uv sync --locked --no-dev

# 3. Run as a normal user, not root
RUN useradd --create-home --uid 1000 appuser
USER appuser

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "niyam.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
