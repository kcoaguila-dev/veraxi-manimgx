"""Unit tests for Veraxi-ManimGX pipeline."""

from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock

from veraxi_manimgx.core.models import (
    Storyboard,
    ScriptBeat,
    EvidenceCitation,
    FactCheckVerdict,
)
from veraxi_manimgx.core.fact_gate import FactGate
from veraxi_manimgx.generators.manim_generator import ManimCodeGenerator


def test_storyboard_grounding_calculation():
    cit = EvidenceCitation(
        source="Financial Shenanigans",
        page=56,
        verbatim_quote="Keurig changed recognition rules.",
    )
    beat1 = ScriptBeat(
        id="b1",
        narration="Keurig [altered] revenue rules.",
        citations=[cit],
        grounding_score=0.95,
        verified=True,
    )
    beat2 = ScriptBeat(
        id="b2",
        narration="Stock prices plummeted.",
        citations=[],
        grounding_score=0.85,
        verified=True,
    )
    sb = Storyboard(
        title="Keurig Case", topic="Revenue Recognition", beats=[beat1, beat2]
    )

    assert sb.is_fully_verified is True
    assert sb.overall_grounding_score == pytest.approx(0.90)


def test_manim_code_generation():
    cit = EvidenceCitation(
        source="Financial Shenanigans",
        page=56,
        verbatim_quote="Keurig changed recognition rules.",
    )
    beat = ScriptBeat(
        id="b1",
        narration="Keurig [altered] its revenue rules.",
        citations=[cit],
        grounding_score=0.95,
        verified=True,
    )
    sb = Storyboard(title="Keurig Shenanigans", topic="Accounting", beats=[beat])

    gen = ManimCodeGenerator(scene_name="KeurigScene")
    code = gen.generate_code(sb)

    assert "class KeurigScene(Scene):" in code
    assert "ProofCard(" in code
    assert "Financial Shenanigans" in code
    assert "page_number=56" in code
    assert "self.say(" in code


def test_fact_gate_audit():
    async def _run():
        mock_client = AsyncMock()
        mock_client.fact_check.return_value = FactCheckVerdict(
            claim="Keurig altered rules",
            passed=True,
            score=0.92,
            threshold=0.75,
            citations=[],
        )

        gate = FactGate(client=mock_client, threshold=0.75)
        beat = ScriptBeat(
            id="b1", narration="Keurig altered rules", claims=["Keurig altered rules"]
        )
        sb = Storyboard(title="Test", topic="Test", beats=[beat])

        audited = await gate.audit_storyboard(sb, strict=False)
        assert audited.is_fully_verified is True
        assert audited.beats[0].grounding_score == 0.92

    asyncio.run(_run())
