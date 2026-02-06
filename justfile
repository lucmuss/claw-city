set shell := ["bash", "-c"]

default:
    @just --list

# Initializes the project (uv-based)
setup:
    uv venv
    uv sync --extra dev
    cp -n .env.example .env || true

# Starts development environment (runs entrypoint.sh)
dev:
    bash docker/entrypoint.sh

# Formats code (Ruff)
format:
    uv run --with black black src tests
    uv run ruff check --fix src tests

# Checks code quality (read-only)
lint:
    uv run ruff check src tests
    uv run --with black black --check src tests
    uv run --with flake8 flake8 src tests

# Type-checking
typecheck:
    uv run mypy src

# Runs tests
test:
    uv run pytest

# Full quality check (CI simulation)
check: lint typecheck test

# Build artifacts
build:
    uv run --with build python -m build
    uv run --with twine twine check dist/*

# Full local CI (includes build)
ci: check build

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
    rm -rf .pytest_cache .coverage htmlcov .ruff_cache .mypy_cache dist build
