# Opening Sequence

The opening sequence is an optional intro clip that is prepended to a full
episode when `assets/intro.mp4` exists.

## How it works

- The pipeline detects `assets/intro.mp4`.
- The clip is normalized to match scene settings.
- The clip is concatenated with scene videos into the final episode.

## Replace the intro

1. Export a new `intro.mp4` at 1920x1080, 25fps.
2. Place it in `assets/intro.mp4`.
3. Run a full build and validate the output.
