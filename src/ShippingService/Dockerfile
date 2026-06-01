FROM python:3.13-slim as builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

FROM python:3.13-slim

WORKDIR /app

COPY . .

COPY --from=builder /app/.venv /app/.venv

ENV PYTHONDONTWRITEBYTECODE 1
ENV PATH="/app/.venv/bin:$PATH"

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]