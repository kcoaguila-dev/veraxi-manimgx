"""Generates executable Python ManimGX scene scripts from verified Storyboard models."""

from __future__ import annotations

from veraxi_manimgx.core.models import Storyboard, ScriptBeat


class ManimCodeGenerator:
    """Compiles verified storyboards into production ManimGX Python code."""

    def __init__(self, scene_name: str = "ForensicExplainerScene") -> None:
        self.scene_name = scene_name

    def generate_code(self, storyboard: Storyboard) -> str:
        """Converts storyboard into executable ManimGX scene script."""
        lines = [
            '"""',
            f"Generated ManimGX Scene: {storyboard.title}",
            f"Overall Grounding Score: {storyboard.overall_grounding_score:.2f} (Verified: {storyboard.is_fully_verified})",
            '"""',
            "from manimgx import *",
            "from veraxi_manimgx.voice.kokoro import synthesize_speech",
            "from veraxi_manimgx.templates.proof_card import ProofCard",
            "",
            "config.pixel_width = 1920",
            "config.pixel_height = 1080",
            "config.frame_rate = 60",
            "",
            f"class {self.scene_name}(Scene):",
            "    voice = staticmethod(synthesize_speech)",
            "",
            "    def construct(self) -> None:",
            "        # Initial stage setup",
            "        title_banner = Text(",
            f'            "{storyboard.title}",',
            "            font_size=38,",
            "            color=GOLD,",
            "            weight='BOLD',",
            "        ).to_corner(UL, buff=0.5)",
            "        self.add(title_banner)",
            "",
        ]

        for idx, beat in enumerate(storyboard.beats, start=1):
            lines.extend(self._compile_beat(beat, idx))

        lines.extend(
            [
                "        self.wait(2.0)",
                "",
                'if __name__ == "__main__":',
                "    # Run via CLI: manimgx render this_file.py",
                "    pass",
            ]
        )
        return "\n".join(lines)

    def _compile_beat(self, beat: ScriptBeat, index: int) -> list[str]:
        code = [
            f"        # --- Beat {index}: {beat.id} (Grounding: {beat.grounding_score:.2f}) ---",
        ]

        # Check if this beat features a verified evidence proof card
        card_var = f"proof_card_{index}"
        has_card = False

        if beat.citations:
            citation = beat.citations[0]
            clean_quote = citation.verbatim_quote.replace('"', '\\"').replace("\n", " ")
            clean_source = citation.source.replace('"', '\\"')
            page_val = citation.page if citation.page is not None else "None"

            code.extend(
                [
                    f"        {card_var} = ProofCard(",
                    f'            document_title="{clean_source}",',
                    f"            page_number={page_val},",
                    f'            quote="{clean_quote}",',
                    "        ).move_to(ORIGIN).shift(0.5 * DOWN)",
                ]
            )
            has_card = True

        # Extract bracketed spans in narration for animation binding
        escaped_narration = beat.narration.replace('"', '\\"')

        if has_card:
            code.extend(
                [
                    "        self.say(",
                    f'            "{escaped_narration}",',
                    f"            FadeIn({card_var}, shift=0.3 * UP),",
                    "        )",
                    f"        self.play(FadeOut({card_var}, shift=0.2 * DOWN), run_time=0.6)",
                ]
            )
        else:
            code.extend(
                [
                    "        self.say(",
                    f'            "{escaped_narration}",',
                    "        )",
                ]
            )

        code.append("        self.wait(0.5)")
        code.append("")
        return code
