#!/bin/bash
set -e

echo "Starting Claw City..."

# Optional: Run tests if RUN_TESTS is set to true
if [ "$RUN_TESTS" = "true" ]; then
    echo "Running tests..."
    uv run python -m pytest tests/ -v --tb=short
    echo "Tests passed."
fi

# Run the application
echo "Claw City is ready."
uv run python -m clawcity.cli.main --help
