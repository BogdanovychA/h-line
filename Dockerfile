FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 900 appuser && \
    useradd -u 900 -g appuser -m -s /bin/bash appuser

WORKDIR /app

ENV TZ=Europe/Kyiv

COPY pyproject.toml uv.lock .python-version ./

RUN uv sync --frozen --no-dev --no-install-project

COPY . .

RUN uv sync --frozen --no-dev && chown -R appuser:appuser /app

ENV PATH="/app/.venv/bin:$PATH"

USER appuser

EXPOSE 8080

CMD ["flet", "run", "--web", "--host", "0.0.0.0", "--port", "8080"]
