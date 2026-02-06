# Pipeline

This document describes the end to end pipeline for building an episode.

## Stages

1. Setup
2. Images
3. Audio
4. Video
5. Full

## Inputs

- Episode scripts in `scripts/`
- Character definitions in `data/characters/`
- Location definitions in `data/locations/`
- Visual style in `data/config/visual_style.yaml`
- Environment variables in `.env`

## Outputs

- Images: `output/epXX/images/`
- Audio: `output/epXX/audio_openai/` or `output/epXX/audio_edge/`
- Video: `output/epXX/video/`
- Full episode: `output/epXX/EPXX_FULL.mp4`

## Commands

```bash
uv run clawcity build --episode 1
uv run clawcity build --episode 1 --stage images audio
uv run clawcity build --episode 1 --audio-engine edge
```

## Notes

- Run with `--clean` to remove existing output for an episode.
- Use `--force` to regenerate existing files.
