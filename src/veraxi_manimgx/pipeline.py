"""End-to-end production pipeline orchestrating Veraxi research and ManimGX scene compilation."""

from __future__ import annotations

import logging

from veraxi_manimgx.client.veraxi_client import VeraxiClient
from veraxi_manimgx.core.fact_gate import FactGate
from veraxi_manimgx.core.models import Storyboard, ScriptBeat
from veraxi_manimgx.generators.manim_generator import ManimCodeGenerator

logger = logging.getLogger(__name__)


class ProductionPipeline:
    """Orchestrates research, fact verification, and Manim code compilation."""

    def __init__(
        self,
        client: VeraxiClient | None = None,
        threshold: float = 0.70,
    ) -> None:
        self.client = client or VeraxiClient()
        self.fact_gate = FactGate(client=self.client, threshold=threshold)
        self.generator = ManimCodeGenerator()

    async def create_storyboard_from_research(
        self, topic: str, max_beats: int = 3
    ) -> Storyboard:
        """Searches Veraxi GraphRAG and structures evidence into narrative beats."""
        citations = await self.client.hybrid_search(topic, limit=max_beats)

        beats: list[ScriptBeat] = []
        for idx, cit in enumerate(citations, start=1):
            # Clean snippet for voice script
            clean_quote = cit.verbatim_quote.strip().replace("\n", " ")
            clean_quote = clean_quote[:120] if len(clean_quote) > 120 else clean_quote

            narration = f"According to primary sources, [{cit.source[:30]}] documented that [{clean_quote}]."
            beat = ScriptBeat(
                id=f"beat_{idx}",
                narration=narration,
                claims=[f"{cit.source[:30]} stated that {clean_quote}"],
                citations=[cit],
                estimated_duration_sec=6.0,
            )
            beats.append(beat)

        return Storyboard(
            title=f"Forensic Investigation: {topic}",
            topic=topic,
            beats=beats,
        )

    async def run(
        self, topic: str, strict_audit: bool = False
    ) -> tuple[Storyboard, str]:
        """
        Executes complete production workflow:
        1. Research via Veraxi MCP
        2. Audit through Fact Gate
        3. Compile to ManimGX Python code
        """
        logger.info(f"Researching topic on Veraxi: {topic}")
        storyboard = await self.create_storyboard_from_research(topic)

        logger.info("Auditing storyboard claims against knowledge base...")
        audited_storyboard = await self.fact_gate.audit_storyboard(
            storyboard, strict=strict_audit
        )

        logger.info("Compiling verified storyboard to ManimGX scene script...")
        manim_code = self.generator.generate_code(audited_storyboard)

        return audited_storyboard, manim_code
