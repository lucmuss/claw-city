import yaml
import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from clawcity.core.models import Scene, DialogueLine

@dataclass
class Location:
    name: str
    description: str
    visual_modifiers: List[str] = field(default_factory=list)


def load_yaml_file(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def load_style_prefix() -> str:
    config_path = "data/config/visual_style.yaml"
    config = load_yaml_file(config_path)
    return config.get("style_prefix", "")

def load_character(character_name: str) -> dict:
    char_path = os.path.join("data", "characters", f"{character_name.lower()}.yaml")
    if not os.path.exists(char_path):
        # Fallback if character-specific YAML not found
        return {"name": character_name, "visual": {"species": "unknown creature"}}
    return load_yaml_file(char_path)

def load_location(location_name: str) -> dict:
    loc_path = os.path.join("data", "locations", f"{location_name.lower().replace(' ', '_')}.yaml")
    if not os.path.exists(loc_path):
        loc_path = os.path.join("data", "locations", "default.yaml") # Fallback to default location
    return load_yaml_file(loc_path)

def build_image_prompt(scene: Scene, previous_scene: Optional[Scene] = None) -> str:
    parts = []

    # 1. Globaler Stil (immer)
    parts.append(load_style_prefix())

    # 2. Charaktere in Szene (detailliert)
    # Assuming scene.characters will be a list of character names present in the dialogue or otherwise specified
    characters_in_scene = set(d.character for d in scene.dialogue)
    for char_name in characters_in_scene:
        char_def = load_character(char_name)

        # Build visual description from loaded character data
        visual_desc_parts = []
        for key, value in char_def.get("visual", {}).items():
            visual_desc_parts.append(f"{key}: {value}")
        if visual_desc_parts:
            parts.append(f"{char_def['name']}: {', '.join(visual_desc_parts)}")

    # 3. Location
    location_data = load_location(scene.location)
    parts.append(location_data.get("description", scene.location))

    # 4. Kontext vorherige Szene (optional)
    if previous_scene and previous_scene.visual_summary:
        parts.append(f"Continuation: {previous_scene.visual_summary}")

    # 5. Aktuelle Szene-Aktion
    parts.append(scene.image_prompt)

    return " | ".join(filter(None, parts))
