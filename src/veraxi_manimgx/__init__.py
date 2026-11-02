"""Veraxi-ManimGX: Grounded forensic animation pipeline bridging Veraxi GraphRAG with ManimGX."""

from __future__ import annotations

from veraxi_manimgx.client.veraxi_client import VeraxiClient
from veraxi_manimgx.core.fact_gate import FactGate
from veraxi_manimgx.core.models import (
    EvidenceCitation,
    FactCheckVerdict,
    ScriptBeat,
    Storyboard,
    VisualElement,
    VisualType,
)
from veraxi_manimgx.generators.manim_generator import ManimCodeGenerator
from veraxi_manimgx.pipeline import ProductionPipeline

__version__ = "0.1.0"

__all__ = [
    "EvidenceCitation",
    "FactCheckVerdict",
    "FactGate",
    "ManimCodeGenerator",
    "ProductionPipeline",
    "ScriptBeat",
    "Storyboard",
    "VeraxiClient",
    "VisualElement",
    "VisualType",
    "__version__",
]
