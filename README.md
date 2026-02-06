# Claw City

Claw City is a modular pipeline for generating AI assisted comedy episodes with images, audio, and video.

## Repository layout

```
claw-city/
|-- src/
|   `-- clawcity/
|-- configs/
|-- data/
|-- assets/
|-- scripts/
|-- docs/
|-- examples/
|-- docker/
|-- tests/
|-- pyproject.toml
|-- uv.lock
|-- justfile
`-- README.md
```

## Installation

Requirements:
- Python 3.11+
- uv
- FFmpeg

Setup:

```bash
uv venv
uv sync --extra dev
cp .env.example .env
```

## Configuration

Environment variables:
- `OPENAI_API_KEY`
- `REPLICATE_API_TOKEN`
- `TTS_PROVIDER` (openai or edge)
- `IMAGE_PROVIDER` (replicate by default)

Optional overrides:
- `OPENAI_TTS_MODEL`
- `OPENAI_TTS_VOICE`
- `EDGE_TTS_VOICE`
- `IMAGE_ASPECT_RATIO`
- `IMAGE_OUTPUT_FORMAT`
- `IMAGE_OUTPUT_QUALITY`
- `RATE_LIMIT_DELAY`
- `MAX_RETRIES`
- `MAX_WORKERS`

Edit `configs/pipeline_settings.yaml` for project level defaults.

## Usage

```bash
uv run clawcity build --episode 1
uv run clawcity build --episode 1 --stage images audio
uv run clawcity build --episode 1 --audio-engine edge
uv run clawcity status --episode 1
uv run clawcity clean --episode 1 --yes
```

## Examples

- `examples/episode_script_minimal.yaml` provides a minimal episode script.

## Development workflow

```bash
just setup
just format
just lint
just test
just check
just ci
```

Pre-commit hooks:

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

## Release steps

1. Update the version in `pyproject.toml`.
2. Update documentation in `docs/`.
3. Run `just ci` locally.
4. Tag the release: `git tag vX.Y.Z`.
5. Push tags: `git push origin --tags`.

GitHub Actions will publish to PyPI on `v*.*.*` tags and build binaries for releases.

## Troubleshooting

- Missing API keys: ensure `.env` contains `OPENAI_API_KEY` and `REPLICATE_API_TOKEN`.
- FFmpeg not found: install FFmpeg and verify `ffmpeg -version` works.
- Edge TTS not available: run `uv add edge-tts` and retry.
- OpenAI SDK missing: run `uv add openai` and retry.
