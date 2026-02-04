set shell := ["bash", "-c"]

default:
    @just --list

# Initializes the project (uv-based)
setup:
    uv sync
    cp -n .env.example .env || true

# Starts development environment (runs entrypoint.sh)
dev:
    bash docker/entrypoint.sh

# Formats code (Ruff)
format:
    uv run ruff format clawcity tests
    uv run ruff check --fix clawcity tests

# Checks code quality (read-only)
lint:
    uv run ruff check clawcity tests
    uv run ruff format --check clawcity tests

# Type-checking
typecheck:
    uv run mypy clawcity

# Runs tests
test:
    uv run pytest

# Full quality check (CI simulation)
check: lint typecheck test

# Starts Docker containers (deployment testing)
docker-up:
    docker-compose up -d --build
    docker-compose logs -f

# Stops Docker containers
docker-down:
    docker-compose down

# Cleans artifacts
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    rm -rf .pytest_cache .coverage htmlcov .ruff_cache