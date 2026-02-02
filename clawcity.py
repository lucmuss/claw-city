#!/usr/bin/env python3
"""
Claw City - One-Command Pipeline
Einfacher Einstiegspunkt für die komplette Pipeline

Usage:
    python clawcity.py --episode 1              # Full pipeline
    python clawcity.py --episode 1 --full       # Mit Full Episode
    python clawcity.py --episode 1 --stage images audio  # Nur bestimmte Stages
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Lade Umgebungsvariablen aus .env-Datei
# Muss VOR dem Import von 'clawcity.core.config' erfolgen.
load_dotenv()

from clawcity.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
