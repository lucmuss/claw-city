# -*- coding: utf-8 -*-
"""Unit tests for core models."""

from pathlib import Path

from clawcity.core.models import Episode, PipelineContext, Scene


def test_scene_duration_seconds_parses_int():
    scene = Scene(
        id=1,
        title="Test",
        location="Cafe",
        time="morning",
        duration="25 sec",
        image_prompt="Test",
        dialogue=[],
    )
    assert scene.duration_seconds == 25


def test_scene_duration_seconds_defaults_on_invalid():
    scene = Scene(
        id=1,
        title="Test",
        location="Cafe",
        time="morning",
        duration="unknown",
        image_prompt="Test",
        dialogue=[],
    )
    assert scene.duration_seconds == 10


def test_pipeline_context_paths():
    episode = Episode(number=1, title="Test")
    context = PipelineContext(episode=episode, output_dir=Path("output/ep01"))
    assert (
        context.get_image_path(1).as_posix().endswith("output/ep01/images/scene_01.png")
    )
    assert (
        context.get_video_path(2).as_posix().endswith("output/ep01/video/scene_02.mp4")
    )
