"""Unit tests for Veraxi-ManimGX pipeline."""

from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock

from veraxi_manimgx.core.models import (
    EvaluationStrategy,
    EvidenceCitation,
    FactCheckVerdict,
    ScriptBeat,
    Storyboard,
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


def test_hybrid_fact_gate_success():
    async def _run():
        gate = FactGate(strategy=EvaluationStrategy.HYBRID)
        cit = EvidenceCitation(
            source="Fooling Some of the People",
            page=81,
            verbatim_quote="Allied accrued non-cash PIK interest on mezzanine loans.",
            chunk_text="Allied accrued non-cash PIK interest on mezzanine loans to report income.",
        )
        # Paraphrased narration without word-for-word clone
        beat = ScriptBeat(
            id="beat_1",
            narration="Allied Capital [booked paper profits] using [payment-in-kind loans].",
            citations=[cit],
        )
        verified_beat = await gate.verify_beat(beat)
        assert verified_beat.verified is True
        assert verified_beat.anchor_verified is True
        assert verified_beat.semantic_verified is True
        assert verified_beat.grounding_score >= 0.90

    asyncio.run(_run())


def test_negation_polarity_detection():
    async def _run():
        gate = FactGate(strategy=EvaluationStrategy.HYBRID)
        cit = EvidenceCitation(
            source="Fooling Some of the People",
            page=81,
            verbatim_quote="Allied capitalized PIK interest onto loan balances.",
        )
        # Unfaithful narration introducing negation opposite to evidence
        beat = ScriptBeat(
            id="beat_neg",
            narration="Allied Capital [never capitalized] PIK interest onto loan balances.",
            citations=[cit],
        )
        verified_beat = await gate.verify_beat(beat)
        assert verified_beat.semantic_verified is False
        assert verified_beat.verified is False
        assert "negation" in verified_beat.semantic_reasoning.lower()

    asyncio.run(_run())
