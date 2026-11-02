"""Command line interface for Veraxi-ManimGX."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from veraxi_manimgx.client.veraxi_client import VeraxiClient
from veraxi_manimgx.pipeline import ProductionPipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Veraxi-ManimGX: Grounded forensic animation generator."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Command: stats
    subparsers.add_parser("stats", help="Check Veraxi database statistics.")

    # Command: generate
    gen_parser = subparsers.add_parser("generate", help="Research and generate a ManimGX scene script.")
    gen_parser.add_argument("topic", type=str, help="Research topic or case study.")
    gen_parser.add_argument("-o", "--output", type=str, default="scene.py", help="Output Python script path.")
    gen_parser.add_argument("--beats", type=int, default=3, help="Number of narrative beats.")

    args = parser.parse_args()

    if args.command == "stats":
        asyncio.run(_cmd_stats())
    elif args.command == "generate":
        asyncio.run(_cmd_generate(args.topic, args.output, args.beats))


async def _cmd_stats() -> None:
    client = VeraxiClient()
    print("Connecting to Veraxi MCP server...")
    stats = await client.get_stats()
    print("Database Statistics:")
    print(json.dumps(stats, indent=2))


async def _cmd_generate(topic: str, output_path: str, beats: int) -> None:
    pipeline = ProductionPipeline()
    print(f"🎬 Initiating Veraxi-ManimGX production for: '{topic}'")
    storyboard, code = await pipeline.run(topic)

    print(f"✅ Storyboard generated: {len(storyboard.beats)} beats")
    print(f"🛡️ Overall Grounding Score: {storyboard.overall_grounding_score:.2f}")

    Path(output_path).write_text(code, encoding="utf-8")
    print(f"💾 ManimGX scene saved to: {output_path}")


if __name__ == "__main__":
    main()
