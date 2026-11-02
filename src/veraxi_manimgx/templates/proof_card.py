"""ProofCard visual component for displaying verified evidence citations in ManimGX."""

from __future__ import annotations

try:
    from manimgx import (
        VGroup,
        RoundedRectangle,
        Text,
        Paragraph,
        BLUE_E,
        GREY_B,
        GOLD,
        WHITE,
        UP,
        DOWN,
        LEFT,
        RIGHT,
        ORIGIN,
        UL,
        UR,
        FadeIn,
        FadeOut,
        Indicate,
    )
except ImportError:
    # Graceful fallback if manimgx is not installed in the current environment
    class VGroup:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def add(self, *args):
            return self

        def move_to(self, *args):
            return self

        def shift(self, *args):
            return self

        def scale(self, *args):
            return self


class ProofCard(VGroup):
    """
    An animated forensic evidence card that renders verbatim quotes,
    source document title, and page number on the Manim stage.
    """

    def __init__(
        self,
        document_title: str,
        page_number: int | None,
        quote: str,
        width: float = 12.0,
        height: float = 3.6,
        color=BLUE_E,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        # Background Plate
        self.bg = RoundedRectangle(
            corner_radius=0.2,
            width=width,
            height=height,
            fill_color=color,
            fill_opacity=0.85,
            stroke_color=GOLD,
            stroke_width=2.5,
        )
        self.add(self.bg)

        # Title & Document Header
        truncated_title = (
            document_title[:55] + "..." if len(document_title) > 55 else document_title
        )
        self.header = (
            Text(
                f"VERIFIED EVIDENCE: {truncated_title}",
                font_size=20,
                color=GOLD,
                weight="BOLD",
            )
            .move_to(self.bg.get_corner(UL))
            .shift(0.4 * DOWN + 0.4 * RIGHT)
        )
        self.add(self.header)

        # Page Number Badge
        page_label = f"PAGE {page_number}" if page_number else "EXHIBIT"
        self.badge = (
            Text(
                page_label,
                font_size=18,
                color=WHITE,
                weight="BOLD",
            )
            .move_to(self.bg.get_corner(UR))
            .shift(0.4 * DOWN + 0.5 * LEFT)
        )
        self.add(self.badge)

        # Verbatim Proof Quote Body
        clean_quote = f'"{quote.strip()}"'
        if len(clean_quote) > 180:
            clean_quote = clean_quote[:177] + '..."'

        self.quote_text = (
            Paragraph(
                clean_quote,
                font_size=22,
                line_spacing=0.8,
                color=WHITE,
                alignment="left",
            )
            .move_to(self.bg.get_center())
            .shift(0.2 * DOWN)
        )
        self.add(self.quote_text)
