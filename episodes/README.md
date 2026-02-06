# Episodes

This folder contains scripts and production assets for episodes.

## Structure

```
episodes/
|-- season_01/
|   |-- pilot/
|   |   |-- script.md
|   |   `-- prompts.md
|   |-- e02_new_holiday/
|   |-- e03_big_catch/
|   `-- ...
`-- templates/
    `-- episode_template.md
```

## Episode status

| Episode | Title | Status | Script | Prompts |
|---------|-------|--------|--------|---------|
| S01E01 | The Token Counter | Done | Yes | No |
| S01E02 | The New Holiday | Planned | No | No |
| S01E03 | Berthold Big Catch | Planned | No | No |
| S01E04 | Helga Says No | Planned | No | No |
| S01E05 | The Grill Duel | Planned | No | No |
| S01E06 | Sabrina Means It | Planned | No | No |

## Episode template

```bash
mkdir episodes/season_01/eXX_title
cp episodes/templates/episode_template.md episodes/season_01/eXX_title/script.md
```

## Format

Each episode may include:
- `script.md` for the full script
- `prompts.md` for scene prompts
- `metadata.json` for episode metadata
