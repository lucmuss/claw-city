#!/usr/bin/env python3
"""
Claw City CLI - Modular Pipeline for AI-Generated Comedy Show

Usage:
    python -m clawcity.cli.main build --episode 1
    python -m clawcity.cli.main build --episode 1 --audio-engine edge
    python -m clawcity.cli.main build --episode 1 --stage images audio
"""
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from clawcity.pipeline.engine import (
    get_pipeline, PipelineStage, PipelineEngine
)
from clawcity.core.exceptions import ClawCityError


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser"""
    parser = argparse.ArgumentParser(
        prog="clawcity",
        description="Claw City - AI Comedy Show Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s build --episode 1                    # Full pipeline
  %(prog)s build --episode 1 --full             # Include full episode
  %(prog)s build --episode 1 --audio-engine edge # Use Edge TTS
  %(prog)s build --episode 1 --stage images     # Only images
  %(prog)s status --episode 1                   # Check episode status
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Build command
    build_parser = subparsers.add_parser(
        "build",
        help="Build an episode",
        description="Generate images, audio, and video for an episode"
    )
    build_parser.add_argument(
        "--episode", "-e",
        type=int,
        required=True,
        help="Episode number"
    )
    build_parser.add_argument(
        "--script", "-s",
        type=Path,
        help="Path to script YAML file"
    )
    build_parser.add_argument(
        "--stage",
        nargs="+",
        choices=["images", "audio", "video", "full"],
        help="Stages to run (default: all)"
    )
    build_parser.add_argument(
        "--audio-engine",
        choices=["openai", "edge"],
        default="openai",
        help="TTS engine (default: openai)"
    )
    build_parser.add_argument(
        "--full", "-f",
        action="store_true",
        help="Include full episode combination"
    )
    build_parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate existing files"
    )
    build_parser.add_argument(
        "--clean", "-c",
        action="store_true",
        help="Delete existing episode files before generation"
    )
    
    # Status command
    status_parser = subparsers.add_parser(
        "status",
        help="Check episode status"
    )
    status_parser.add_argument(
        "--episode", "-e",
        type=int,
        required=True,
        help="Episode number"
    )
    
    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Show episode information"
    )
    info_parser.add_argument(
        "--episode", "-e",
        type=int,
        required=True,
        help="Episode number"
    )
    
    # Clean command
    clean_parser = subparsers.add_parser(
        "clean",
        help="Clean episode output"
    )
    clean_parser.add_argument(
        "--episode", "-e",
        type=int,
        required=True,
        help="Episode number"
    )
    clean_parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation"
    )
    
    return parser


def cmd_build(args) -> int:
    """Execute build command"""
    try:
        pipeline = get_pipeline()
        
        # Determine stages
        stages = []
        if args.stage:
            stage_map = {
                "images": PipelineStage.IMAGES,
                "audio": PipelineStage.AUDIO,
                "video": PipelineStage.VIDEO,
                "full": PipelineStage.FULL,
            }
            stages = [stage_map[s] for s in args.stage]
        else:
            stages = [
                PipelineStage.SETUP,
                PipelineStage.IMAGES,
                PipelineStage.AUDIO,
                PipelineStage.VIDEO,
            ]
            if args.full:
                stages.append(PipelineStage.FULL)
        
        # Run pipeline
        results = pipeline.run(
            episode_num=args.episode,
            script_path=args.script,
            stages=stages,
            audio_engine=args.audio_engine,
            skip_existing=not args.force,
            clean=args.clean
        )
        
        # Return exit code based on results
        return 0 if all(r.success for r in results) else 1
        
    except ClawCityError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.audio_engine == "openai":
            print("\n💡 Try using --audio-engine edge for free TTS")
        return 1


def cmd_status(args) -> int:
    """Execute status command"""
    output_dir = Path(f"output/ep{args.episode:02d}")
    
    if not output_dir.exists():
        print(f"❌ Episode {args.episode:02d} not found")
        return 1
    
    print(f"\n📊 Episode {args.episode:02d} Status")
    print("=" * 40)
    
    # Check each stage
    images = list((output_dir / "images").glob("*.png")) if (output_dir / "images").exists() else []
    audio = list((output_dir / "audio_openai").rglob("*.mp3")) if (output_dir / "audio_openai").exists() else []
    videos = list((output_dir / "video").glob("scene_*.mp4")) if (output_dir / "video").exists() else []
    full = list(output_dir.glob("EP*_FULL.mp4"))
    
    print(f"   🖼️  Images: {len(images)}")
    print(f"   🎵 Audio: {len(audio)}")
    print(f"   🎬 Videos: {len(videos)}")
    print(f"   ⭐ Full Episode: {'✓' if full else '✗'}")
    
    return 0


def cmd_info(args) -> int:
    """Execute info command"""
    try:
        pipeline = get_pipeline()
        episode = pipeline.load_episode(args.episode)
        
        print(f"\n📖 Episode {episode.number:02d}: {episode.title}")
        if episode.subtitle:
            print(f"   {episode.subtitle}")
        print("=" * 50)
        print(f"   Scenes: {episode.scene_count}")
        print(f"   Duration: ~{episode.total_duration_seconds // 60} min")
        if episode.tone:
            print(f"   Tone: {episode.tone}")
        if episode.themes:
            print(f"   Themes: {', '.join(episode.themes)}")
        
        print(f"\n🎬 Scenes:")
        for scene in episode.scenes[:5]:
            lines = len(scene.dialogue)
            print(f"   {scene.id}. {scene.title} ({lines} lines)")
        if len(episode.scenes) > 5:
            print(f"   ... and {len(episode.scenes) - 5} more")
        
        return 0
        
    except ClawCityError as e:
        print(f"❌ Error: {e}")
        return 1


def cmd_clean(args) -> int:
    """Execute clean command"""
    output_dir = Path(f"output/ep{args.episode:02d}")
    
    if not output_dir.exists():
        print(f"❌ Episode {args.episode:02d} not found")
        return 1
    
    if not args.yes:
        response = input(f"Delete all files for episode {args.episode:02d}? [y/N] ")
        if response.lower() != "y":
            print("Cancelled")
            return 0
    
    import shutil
    shutil.rmtree(output_dir)
    print(f"✓ Cleaned episode {args.episode:02d}")
    return 0


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point"""
    parser = create_parser()
    parsed = parser.parse_args(args)
    
    if not parsed.command:
        parser.print_help()
        return 1
    
    # Dispatch commands
    commands = {
        "build": cmd_build,
        "status": cmd_status,
        "info": cmd_info,
        "clean": cmd_clean,
    }
    
    handler = commands.get(parsed.command)
    if handler:
        return handler(parsed)
    
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
