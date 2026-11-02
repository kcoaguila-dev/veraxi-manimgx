"""Grounding Gate: Enforces factual proof on every script beat before rendering."""

from __future__ import annotations

import logging

from veraxi_manimgx.client.veraxi_client import VeraxiClient
from veraxi_manimgx.core.models import ScriptBeat, Storyboard, FactCheckVerdict

logger = logging.getLogger(__name__)


class GroundingGateError(Exception):
    """Raised when one or more script beats fail the grounding threshold."""

    def __init__(self, message: str, failed_verdicts: list[FactCheckVerdict]) -> None:
        super().__init__(message)
        self.failed_verdicts = failed_verdicts


class FactGate:
    """Audits each script beat against the Veraxi knowledge base."""

    def __init__(
        self, client: VeraxiClient | None = None, threshold: float = 0.75
    ) -> None:
        self.client = client or VeraxiClient()
        self.threshold = threshold

    async def verify_beat(self, beat: ScriptBeat) -> ScriptBeat:
        """Verifies all claims in a single script beat."""
        if not beat.claims:
            # If no explicit claims, use the cleaned narration as the claim
            clean_narration = beat.narration.replace("[", "").replace("]", "").strip()
            beat.claims = [clean_narration]

        failed_claims: list[FactCheckVerdict] = []
        scores: list[float] = []

        for claim in beat.claims:
            verdict = await self.client.fact_check(claim, min_score=self.threshold)
            scores.append(verdict.score)
            if not verdict.passed:
                failed_claims.append(verdict)
            else:
                # Attach verified citations to the beat
                for c in verdict.citations:
                    if c not in beat.citations:
                        beat.citations.append(c)

        beat.grounding_score = sum(scores) / max(1, len(scores))
        beat.verified = len(failed_claims) == 0
        return beat

    async def audit_storyboard(
        self, storyboard: Storyboard, strict: bool = True
    ) -> Storyboard:
        """Audits all beats in a storyboard, raising an error if strict is True and any fail."""
        all_failed: list[FactCheckVerdict] = []

        for beat in storyboard.beats:
            await self.verify_beat(beat)
            if not beat.verified:
                for claim in beat.claims:
                    all_failed.append(
                        FactCheckVerdict(
                            claim=claim,
                            passed=False,
                            score=beat.grounding_score,
                            threshold=self.threshold,
                            verdict_text=f"Beat {beat.id} failed grounding verification.",
                        )
                    )

        if strict and all_failed:
            raise GroundingGateError(
                f"Storyboard '{storyboard.title}' failed fact gate: {len(all_failed)} claim(s) unsupported.",
                failed_verdicts=all_failed,
            )

        return storyboard
