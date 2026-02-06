# -*- coding: utf-8 -*-
"""Unit tests for configuration merging."""

from clawcity.core.config import AppConfig


def test_config_merge_updates_output_dir(tmp_path):
    config = AppConfig()
    data = {"output": {"base_dir": str(tmp_path / "out")}}
    config._merge_yaml(data)
    assert config.output_dir == tmp_path / "out"


def test_config_merge_updates_image_suffix():
    config = AppConfig()
    data = {"image_generation": {"prompt_suffix": "test suffix"}}
    config._merge_yaml(data)
    assert config.images.style_suffix == "test suffix"
