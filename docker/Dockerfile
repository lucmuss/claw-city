FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Copy metadata and install dependencies
COPY pyproject.toml uv.lock ./
RUN uv venv && uv sync --extra dev --frozen --no-install-project

# Copy source code
COPY src/ ./src/
COPY configs/ ./configs/
COPY data/ ./data/
COPY assets/ ./assets/
COPY scripts/ ./scripts/

RUN uv sync --extra dev --frozen

# Copy entrypoint
COPY docker/entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

# Set environment
ENV PYTHONPATH=/app/src
ENV RUN_TESTS=false

# Run entrypoint
CMD ["./entrypoint.sh"]
