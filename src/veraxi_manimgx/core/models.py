"""Data models for Veraxi-ManimGX pipeline."""
from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class VisualType(str, Enum):
    PROOF_CARD = "proof_card"
    ENTITY_GRAPH = "entity_graph"
    BALANCE_SHEET = "balance_sheet"
    CHART = "chart"
    MATH_FORMULA = "math_formula"
    CALLOUT = "callout"


class EvidenceCitation(BaseModel):
    """Grounded evidence citation retrieved from Veraxi."""
    id: str | None = None
    source: str
    page: int | None = None
    breadcrumb: str | None = None
    verbatim_quote: str
    chunk_text: str = ""
    score: float | None = None


class EntityRelation(BaseModel):
    """Graph edge between two entities extracted from Neo4j."""
    source_entity: str
    target_entity: str
    relation_type: str
    properties: dict[str, Any] = Field(default_factory=dict)


class FactCheckVerdict(BaseModel):
    """Result of a grounding verification check."""
    claim: str
    passed: bool
    score: float
    threshold: float = 0.8
    citations: list[EvidenceCitation] = Field(default_factory=list)
    verdict_text: str = ""


class VisualElement(BaseModel):
    """Definition of an animated visual component in ManimGX."""
    visual_type: VisualType
    title: str = ""
    subtitle: str = ""
    content: dict[str, Any] = Field(default_factory=dict)
    target_position: str = "ORIGIN"
    scale: float = 1.0


class ScriptBeat(BaseModel):
    """A synchronized narrative scene beat in ManimGX."""
    id: str
    narration: str  # e.g., "Allied Capital [inflated its balance sheet] with [non-cash interest]."
    visuals: list[VisualElement] = Field(default_factory=list)
    claims: list[str] = Field(default_factory=list)
    citations: list[EvidenceCitation] = Field(default_factory=list)
    grounding_score: float = 1.0
    verified: bool = True
    estimated_duration_sec: float = 5.0


class Storyboard(BaseModel):
    """Complete documentary/explainer project storyboard."""
    title: str
    topic: str
    beats: list[ScriptBeat] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def total_estimated_duration(self) -> float:
        return sum(b.estimated_duration_sec for b in self.beats)

    @property
    def overall_grounding_score(self) -> float:
        if not self.beats:
            return 0.0
        return sum(b.grounding_score for b in self.beats) / len(self.beats)

    @property
    def is_fully_verified(self) -> bool:
        return all(b.verified for b in self.beats)
