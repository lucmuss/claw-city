# Claw City - Modular Pipeline v2.0

## Übersicht

Vollständig modularisierte Pipeline für die Generierung von AI-Comedy-Episoden.

## Neue Architektur

```
clawcity/
├── core/                    # Kern-Module
│   ├── models.py           # Datenmodelle (Episode, Scene, Character)
│   ├── config.py           # Konfigurationsmanagement
│   └── exceptions.py       # Custom Exceptions
├── services/               # Service-Layer
│   ├── audio.py           # TTS (OpenAI + Edge)
│   ├── images.py          # Bildgenerierung (Replicate/Flux)
│   └── video.py           # Video-Erstellung (FFmpeg)
├── pipeline/              # Pipeline-Engine
│   └── engine.py          # Orchestration
└── cli/                   # Command-Line Interface
    └── main.py            # CLI-Commands
```

## One-Command Pipeline

### Komplette Episode generieren
```bash
# Full pipeline (Bilder + Audio + Video)
python3 clawcity.py build --episode 1

# Mit Full Episode Kombination
python3 clawcity.py build --episode 1 --full

# Nur bestimmte Stages
python3 clawcity.py build --episode 1 --stage images audio
```

### Alternative: Python Modul
```bash
python3 -m clawcity build --episode 1 --full
```

## CLI Commands

| Command | Beschreibung |
|---------|--------------|
| `build` | Episode generieren |
| `status` | Status prüfen |
| `info` | Episode-Info anzeigen |
| `clean` | Output löschen |

### Build Optionen

```bash
python3 clawcity.py build \
  --episode 1 \              # Episoden-Nummer (required)
  --audio-engine openai \    # TTS: openai oder edge
  --full \                   # Full Episode kombinieren
  --force \                  # Existierende Dateien überschreiben
  --stage images audio       # Nur bestimmte Stages
```

## Konfiguration

### Umgebungsvariablen (.env)
```bash
# API Keys
OPENAI_API_KEY=sk-...
REPLICATE_API_TOKEN=r8_...

# TTS Einstellungen
TTS_PROVIDER=openai          # oder "edge"
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=alloy
EDGE_TTS_VOICE=de-DE-ConradNeural

# Bildgenerierung
IMAGE_PROVIDER=replicate
RATE_LIMIT_DELAY=12
MAX_RETRIES=3

# Video
VIDEO_WIDTH=1920
VIDEO_HEIGHT=1080
SCENE_DURATION=8
```

## Migration von Legacy

| Alt | Neu |
|-----|-----|
| `python pipeline.py --episode 1` | `python3 clawcity.py build --episode 1` |
| `python tts_openai.py --episode 1` | `python3 clawcity.py build --episode 1 --stage audio` |
| `python generate_images_retry.py --episode 1` | `python3 clawcity.py build --episode 1 --stage images` |
| `python create_video.py --episode 1` | `python3 clawcity.py build --episode 1 --stage video` |

## Code-Beispiele

### Programmatische Nutzung
```python
from clawcity.pipeline.engine import get_pipeline, PipelineStage

pipeline = get_pipeline()

# Einzelne Stage
result = pipeline.run_stage(
    PipelineStage.IMAGES,
    context
)

# Komplette Pipeline
results = pipeline.run(
    episode_num=1,
    audio_engine="openai"
)
```

### Custom Service
```python
from clawcity.services.audio import get_audio_service

audio = get_audio_service()
result = await audio.generate_line(
    text="Hallo Welt!",
    character="max",
    output_path=Path("output.mp3")
)
```

## Vorteile der neuen Architektur

1. **Modular** - Jeder Service unabhängig testbar
2. **Erweiterbar** - Neue Services einfach hinzufügen
3. **Konfigurierbar** - Alles über Env-Variablen/YAML
4. **Robust** - Retry-Logik und Fehlerbehandlung
5. **Flexibel** - Einzelne Stages oder komplette Pipeline
