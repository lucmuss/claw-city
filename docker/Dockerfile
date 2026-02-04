FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy pyproject.toml and install dependencies
COPY pyproject.toml ./
RUN uv sync --frozen --no-install-project

# Copy source code
COPY clawcity/ ./clawcity/
COPY configs/ ./configs/
COPY data/ ./data/

# Copy entrypoint
COPY docker/entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

# Set environment
ENV PYTHONPATH=/app
ENV RUN_TESTS=true

# Run entrypoint
CMD ["./entrypoint.sh"]