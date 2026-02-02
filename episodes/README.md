# Episoden

Dieser Ordner enthält alle Skripte und Produktionsunterlagen für Claw City Episoden.

## Struktur

```
episodes/
├── season_01/
│   ├── pilot/
│   │   ├── script.md
│   │   └── prompts.md
│   ├── e02_new_holiday/
│   ├── e03_big_catch/
│   └── ...
└── templates/
    └── episode_template.md
```

## Episode Status

| Episode | Titel | Status | Script | Prompts |
|---------|-------|--------|--------|---------|
| S01E01 | Der Token-Rechner | ✓ Fertig | ✓ | - |
| S01E02 | Der neue Feiertag | ○ Geplant | - | - |
| S01E03 | Bertholds großer Fang | ○ Geplant | - | - |
| S01E04 | Helga sagt Nein | ○ Geplant | - | - |
| S01E05 | Das Grill-Duell | ○ Geplant | - | - |
| S01E06 | Sabrina macht Ernst | ○ Geplant | - | - |

## Episoden-Template

Neue Episoden erstellen mit:

```bash
mkdir episodes/season_01/eXX_titel
cp episodes/templates/episode_template.md episodes/season_01/eXX_titel/script.md
```

## Format

Jede Episode enthält:
- **script.md** - Vollständiges Drehbuch
- **prompts.md** - Bild-Prompts für jede Szene (optional)
- **metadata.json** - Episoden-Metadaten
