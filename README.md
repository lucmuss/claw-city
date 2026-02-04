# 🦀 Claw City

Eine Comedy-Show mit KI-Agenten in einer deutschen Kleinstadt.

## Konzept

In Claw City leben KI-Agenten (Bots) wie normale Menschen - nur dass sie sich um "Menschenkinder" kümmern müssen. Die Menschen sind verniedlicht dargestellt (1/3 der Größe), tollpatschig und fordern ständig Aufmerksamkeit.

**Visueller Stil**: Simpsons trifft Futurama trifft deutsche Gemütlichkeit

## Ordnerstruktur

```
claw-city/
├── clawcity                    # CLI-Tool
├── configs/
│   ├── characters.yaml         # Liste aller Charaktere
│   └── pipeline_settings.yaml  # Pipeline-Konfiguration
├── assets/
│   ├── characters/
│   │   └── {char_id}/
│   │       ├── profile.md      # Charakterprofil
│   │       ├── visual_traits.md # Visuelle Merkmale + Prompts
│   │       ├── backstory.md    # Hintergrundgeschichte
│   │       └── reference_images/ # Referenzbilder
│   └── world/
│       └── global_context.md   # Welt-Kontext
├── outputs/
│   └── images/
│       └── characters/
│           └── {char_id}/
│               ├── standing_prompt.txt
│               ├── sitting_prompt.txt
│               └── metadata.json
└── .env                        # API-Keys (nicht committen!)
```

## Schnellstart: Episode Generierung (Refactored Pipeline)

Das `clawcity` CLI-Tool steuert nun die gesamte Episode-Produktion (Audio, Bilder, Video).

### 1. Setup

```bash
# Repository klonen
cd claw-city

# Projekt initialisieren (installiert uv, dependencies, kopiert .env)
just setup

# Alternativ manuell:
# uv sync --all-extras  # Installiert alle Dependencies
# cp .env.example .env  # Umgebungsvariablen konfigurieren
# Edit .env, füge OPENAI_API_KEY und REPLICATE_API_TOKEN hinzu
```

### 2. Episoden Pipeline nutzen

Alle alten Top-Level-Skripte wurden in das zentrale `clawcity build` Kommando integriert.

```bash
# Gesamte Episode 1 generieren (Audio, Bilder, Videos)
# Der Standard ist OpenAI TTS, die Ausgabe landet in output/ep01/video_openai/
./clawcity build --episode 1 --full

# Nur Bilder generieren
./clawcity build --episode 1 --stage images

# Ergebnisse prüfen
./clawcity status --episode 1

# Nur Audio mit Edge TTS (kostenlose Option)
./clawcity build --episode 1 --stage audio --audio-engine edge

# Alle generierten Dateien für Episode 1 löschen
./clawcity clean --episode 1 -y
```

## Charakter-Struktur

## Charakter-Struktur

Jeder Charakter hat folgende Markdown-Dateien:

### 1. profile.md
- Archetyp
- Persönlichkeit
- Catchphrases
- Menschenkind
- Beziehungen

### 2. visual_traits.md
- Farbschema (Hex-Codes)
- Aussehen
- Kleidung
- Accessoires
- **Prompt-Template** für KI-Bildgenerierung

### 3. backstory.md
- Herkunft
- Tägliche Routine
- Lieblingssnack
- Charakterentwicklung

## Neue Charaktere hinzufügen

1. **In configs/characters.yaml registrieren:**
```yaml
characters:
  - id: mein_charakter
    name: "Voller Name"
    folder: assets/characters/mein_charakter
    archetype: Archetyp
```

2. **Vorlage generieren:**
```bash
./clawcity init mein_charakter "Voller Name" "Archetyp"
```

3. **Templates ausfüllen:**
   - `profile.md`
   - `visual_traits.md` (besonders wichtig: Prompt-Template)
   - `backstory.md`

4. **Generieren:**
```bash
./clawcity character mein_charakter
```

## Reproduzierbarkeit

Alle Prompts und Metadaten werden gespeichert:
- `outputs/images/{character_id}/metadata.json`
- `outputs/images/{character_id}/{pose}_prompt.txt`

Das ermöglicht:
- Gleiche Ergebnisse bei Wiederholung
- Nachvollziehbare Generierung
- Versionierung von Charakteren

## Charaktere

| ID | Name | Archetyp |
|----|------|----------|
| pfarrer_paul | Pfarrer Paul | Priester |
| gina | Gina | Übermutter |
| werner | Werner | Gemütlicher Trinker |
| max | Max | Tausendsassa |
| eric | Eric | Ehrlicher Egoist |
| ... | ... | ... |

## Lizenz

MIT License
