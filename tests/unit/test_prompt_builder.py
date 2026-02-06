# -*- coding: utf-8 -*-
"""Unit tests for prompt builder helpers."""

from clawcity.pipeline.prompt_builder import build_character_visual_prompt


def test_build_character_visual_prompt_basic():
    char_def = {
        "name": "Test",
        "physical": {
            "breed": "tabby",
            "fur_color": "orange",
            "fur_texture": "short",
            "eyes": "green",
            "body_type": "small",
        },
        "clothing": {"default": "blue jacket", "accessories": "scarf"},
        "unique_identifiers": ["tiny scar"],
        "personality_visual_cues": ["confident posture"],
    }

    prompt = build_character_visual_prompt(char_def)
    assert "tabby" in prompt
    assert "blue jacket" in prompt
    assert "tiny scar" in prompt
