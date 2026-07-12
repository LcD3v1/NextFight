FROM ghcr.io/astral-sh/uv:0.11.28 AS uv

FROM python:3.12.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN groupadd --gid 10001 nextfight \
    && useradd --uid 10001 --gid nextfight --create-home nextfight

COPY --from=uv /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY alembic.ini ./
COPY migrations ./migrations
RUN uv sync --frozen --no-dev \
    && chown -R nextfight:nextfight /app

USER nextfight

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "nextfight.main:app", "--host", "0.0.0.0", "--port", "8000"]
