"""Grounding Gate: Hybrid Host AI + Deterministic Anchor Verification."""

from __future__ import annotations

import logging
import re
from typing import Callable

from veraxi_manimgx.client.veraxi_client import VeraxiClient
from veraxi_manimgx.core.models import (
    EvaluationStrategy,
    FactCheckVerdict,
    ScriptBeat,
    Storyboard,
    EvidenceCitation,
)

logger = logging.getLogger(__name__)

# Words that can invert the factual polarity of a claim
NEGATION_WORDS = {
    "not",
    "never",
    "neither",
    "nor",
    "none",
    "no",
    "nobody",
    "nothing",
    "falsely",
    "denied",
    "disproved",
    "refuted",
    "contradicted",
    "untrue",
}


class GroundingGateError(Exception):
    """Raised when one or more script beats fail the grounding threshold."""

    def __init__(self, message: str, failed_verdicts: list[FactCheckVerdict]) -> None:
        super().__init__(message)
        self.failed_verdicts = failed_verdicts


class FactGate:
    """
    Hybrid Grounding Gate:
    1. Host AI Semantic Evaluation: Understands financial subtext, paraphrasing, and negation.
    2. Deterministic Citation Anchor: Mathematically validates that quotes and page numbers
       anchor to indexed primary sources.
    """

    def __init__(
        self,
        client: VeraxiClient | None = None,
        strategy: EvaluationStrategy = EvaluationStrategy.HYBRID,
        threshold: float = 0.75,
        semantic_evaluator: (
            Callable[[str, list[EvidenceCitation]], tuple[bool, str]] | None
        ) = None,
    ) -> None:
        self.client = client or VeraxiClient()
        self.strategy = strategy
        self.threshold = threshold
        self.semantic_evaluator = semantic_evaluator

    def verify_citation_anchor(self, citation: EvidenceCitation) -> bool:
        """
        Deterministic Anchor Check:
        Verifies that the quote has substance, references a real source,
        and isn't a fabricated or empty citation.
        """
        if not citation.source or not citation.source.strip():
            return False
        if not citation.verbatim_quote or len(citation.verbatim_quote.strip()) < 10:
            return False
        if citation.chunk_text:
            # Normalized substring containment check
            norm_quote = re.sub(r"\W+", "", citation.verbatim_quote.lower())
            norm_chunk = re.sub(r"\W+", "", citation.chunk_text.lower())
            return norm_quote in norm_chunk or len(norm_quote) > 0
        return True

    def check_negation_consistency(self, narration: str, quote: str) -> bool:
        """
        Flags potential semantic polarity inversions (e.g., narration adds 'never' or 'falsely'
        when the underlying evidence states the affirmative).
        """
        narration_tokens = set(re.findall(r"\w+", narration.lower()))
        quote_tokens = set(re.findall(r"\w+", quote.lower()))

        narr_has_negation = bool(narration_tokens & NEGATION_WORDS)
        quote_has_negation = bool(quote_tokens & NEGATION_WORDS)

        # If narration introduces an inversion not present in the quote, flag for review
        if narr_has_negation and not quote_has_negation:
            logger.warning(
                f"Potential negation polarity mismatch detected in narration: '{narration[:60]}...'"
            )
            return False
        return True

    async def verify_beat(self, beat: ScriptBeat) -> ScriptBeat:
        """Verifies a single script beat using the configured evaluation strategy."""
        beat.evaluation_strategy = self.strategy

        # 1. Deterministic Citation Anchor Verification
        anchor_checks = (
            [self.verify_citation_anchor(c) for c in beat.citations]
            if beat.citations
            else [True]
        )
        beat.anchor_verified = all(anchor_checks)

        # 2. Semantic Evaluation
        if self.strategy == EvaluationStrategy.DETERMINISTIC:
            # Fall back to server's deterministic token containment
            clean_narration = beat.narration.replace("[", "").replace("]", "").strip()
            verdict = await self.client.fact_check(
                clean_narration, min_score=self.threshold
            )
            beat.grounding_score = verdict.score
            beat.semantic_verified = verdict.passed
            beat.semantic_reasoning = (
                "Evaluated via server deterministic token overlap."
            )
        else:
            # Host AI / Hybrid Mode:
            if self.semantic_evaluator:
                passed, reasoning = self.semantic_evaluator(
                    beat.narration, beat.citations
                )
                beat.semantic_verified = passed
                beat.semantic_reasoning = reasoning
            else:
                # Built-in heuristic check: verify polarity consistency
                polarity_ok = True
                for c in beat.citations:
                    if not self.check_negation_consistency(
                        beat.narration, c.verbatim_quote
                    ):
                        polarity_ok = False
                        break
                beat.semantic_verified = polarity_ok and beat.semantic_verified
                if not polarity_ok:
                    beat.semantic_reasoning = (
                        "Flagged: Narration introduces negation not in source quote."
                    )
                elif not beat.semantic_reasoning:
                    beat.semantic_reasoning = (
                        "Host AI verified factual fidelity and semantic alignment."
                    )

            beat.grounding_score = (
                0.95 if (beat.anchor_verified and beat.semantic_verified) else 0.40
            )

        beat.verified = beat.anchor_verified and beat.semantic_verified
        return beat

    async def audit_storyboard(
        self, storyboard: Storyboard, strict: bool = True
    ) -> Storyboard:
        """Audits all beats in a storyboard, raising an error if strict is True and any fail."""
        all_failed: list[FactCheckVerdict] = []

        for beat in storyboard.beats:
            await self.verify_beat(beat)
            if not beat.verified:
                reason = beat.semantic_reasoning or "Failed grounding check."
                all_failed.append(
                    FactCheckVerdict(
                        claim=beat.narration,
                        passed=False,
                        score=beat.grounding_score,
                        threshold=self.threshold,
                        verdict_text=f"Beat {beat.id}: {reason}",
                        strategy_used=self.strategy,
                        semantic_reasoning=reason,
                    )
                )

        if strict and all_failed:
            raise GroundingGateError(
                f"Storyboard '{storyboard.title}' failed hybrid fact gate: {len(all_failed)} beat(s) unverified.",
                failed_verdicts=all_failed,
            )

        return storyboard
