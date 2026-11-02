"""Entity network visualizer in ManimGX for displaying Neo4j graph relationships."""
from __future__ import annotations

from typing import Sequence
from veraxi_manimgx.core.models import EntityRelation

try:
    from manimgx import (
        VGroup,
        Circle,
        Text,
        Arrow,
        BLUE,
        YELLOW,
        WHITE,
        GREY_B,
        ORIGIN,
        UP,
        DOWN,
        LEFT,
        RIGHT,
    )
except ImportError:
    class VGroup:  # type: ignore
        def __init__(self, *args, **kwargs): pass
        def add(self, *args): return self


class EntityNode(VGroup):
    """Visual circular node representing an entity in the knowledge graph."""

    def __init__(self, name: str, radius: float = 0.8, color=BLUE, **kwargs) -> None:
        super().__init__(**kwargs)
        self.circle = Circle(radius=radius, color=color, fill_opacity=0.3, stroke_width=3)
        self.label = Text(name[:20], font_size=18, color=WHITE).move_to(self.circle.get_center())
        self.add(self.circle, self.label)


class EntityNetwork(VGroup):
    """
    Renders multi-hop Neo4j paths as an animated network graph.
    """

    def __init__(self, relations: Sequence[EntityRelation], **kwargs) -> None:
        super().__init__(**kwargs)
        self.nodes: dict[str, EntityNode] = {}
        self.arrows: list[VGroup] = []

        # Position root entity at center and surrounding related entities
        entity_names = set()
        for r in relations:
            entity_names.add(r.source_entity)
            entity_names.add(r.target_entity)

        import math
        names_list = list(entity_names)
        radius = 3.5

        for idx, name in enumerate(names_list):
            node = EntityNode(name=name)
            if idx == 0:
                node.move_to(ORIGIN)
            else:
                angle = (2 * math.pi * (idx - 1)) / max(1, len(names_list) - 1)
                node.move_to([radius * math.cos(angle), radius * math.sin(angle), 0])
            self.nodes[name] = node
            self.add(node)

        for r in relations:
            src_node = self.nodes.get(r.source_entity)
            tgt_node = self.nodes.get(r.target_entity)
            if src_node and tgt_node and src_node != tgt_node:
                arrow = Arrow(
                    src_node.circle.get_edge_center(tgt_node.circle.get_center() - src_node.circle.get_center()),
                    tgt_node.circle.get_edge_center(src_node.circle.get_center() - tgt_node.circle.get_center()),
                    buff=0.1,
                    color=YELLOW,
                    stroke_width=2,
                )
                rel_label = Text(r.relation_type, font_size=14, color=GREY_B).next_to(arrow, UP, buff=0.1)
                arrow_group = VGroup(arrow, rel_label)
                self.arrows.append(arrow_group)
                self.add(arrow_group)
