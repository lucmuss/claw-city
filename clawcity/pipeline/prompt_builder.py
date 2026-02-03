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
    with open(filepath, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_style_prefix() -> str:
    config_path = "data/config/visual_style.yaml"
    config = load_yaml_file(config_path)
    return config.get("style_prefix", "")


def load_character(character_name: str) -> dict:
    char_path = os.path.join("data", "characters", f"{character_name.lower()}.yaml")
    if not os.path.exists(char_path):
        return {"name": character_name, "physical": {"breed": "unknown cat"}}
    return load_yaml_file(char_path)


def load_location(location_name: str) -> dict:
    loc_id = location_name.lower()
    loc_id = "".join(c for c in loc_id if c.isalnum())
    loc_path = os.path.join("data", "locations", f"{loc_id}.yaml")
    if not os.path.exists(loc_path):
        loc_path = os.path.join("data", "locations", "default.yaml")
    return load_yaml_file(loc_path)


def build_character_visual_prompt(char_def: dict) -> str:
    visual_parts = []
    phys = char_def.get("physical", {})
    if phys:
        breed = phys.get("breed", "")
        fur = phys.get("fur_color", "")
        texture = phys.get("fur_texture", "")
        eyes = phys.get("eyes", "")
        body = phys.get("body_type", "")
        physical_traits = [body, texture, fur, breed]
        trait_string = ", ".join(filter(None, physical_traits))
        if eyes:
            trait_string += f", with {eyes} eyes"
        visual_parts.append(trait_string.strip())
    clothing = char_def.get("clothing", {})
    if clothing:
        default_outfit = clothing.get("default", "")
        acc = clothing.get("accessories", "")
        if default_outfit and default_outfit.lower() != "none":
            visual_parts.append(f"wearing {default_outfit}")
        if acc and acc.lower() != "none":
            visual_parts.append(f"with {acc}")
    uniques = char_def.get("unique_identifiers", [])
    if uniques:
        visual_parts.extend(uniques)
    traits = char_def.get("personality_visual_cues", [])
    if traits:
        visual_parts.extend(traits)
    return ", ".join(filter(None, visual_parts))


def build_image_prompt(scene: Scene, previous_scenes: Optional[List[Scene]] = None) -> str:
    parts = []
    parts.append(load_style_prefix())
    characters_in_scene = set(d.character for d in scene.dialogue)
    for char_name in characters_in_scene:
        char_def = load_character(char_name)
        char_prompt = build_character_visual_prompt(char_def)
        if char_prompt:
            parts.append(f"{char_def['name']}: {char_prompt}")
    location_data = load_location(scene.location)
    parts.append(location_data.get("description", scene.location))
    if previous_scenes:
        for i, prev in enumerate(reversed(previous_scenes[-2:])):
            if prev.visual_summary:
                label = "Recent context" if i == 0 else "Earlier context"
                parts.append(f"{label}: {prev.visual_summary}")
    action_prompt = scene.image_prompt
    style_removals = [
        "Simpsons cartoon style",
        "Pixar-style 3D animation",
        "Pixar-style",
        "cartoon style",
        "3D animation",
    ]
    for s in style_removals:
        action_prompt = action_prompt.replace(s, "").replace(s.lower(), "")
    parts.append(action_prompt.strip(", "))
    return " | ".join(filter(None, parts))
