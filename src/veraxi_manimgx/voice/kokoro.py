"""Kokoro-82M Text-to-Speech integration for ManimGX."""
from __future__ import annotations

import logging
import os
import re
import sys
import types
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# Lightweight tokenizer fallback if spacy C-extensions are missing on Python 3.14
if "spacy" not in sys.modules:
    spacy_mod = types.ModuleType("spacy")

    @dataclass
    class _SpanToken:
        text: str
        tag_: str
        whitespace_: str

    class _DummyNLP:
        _TOKEN_RE = re.compile(r"(\w+|[^\w\s])(\s*)")

        def __call__(self, text: str) -> list[_SpanToken]:
            out: list[_SpanToken] = []
            for m in self._TOKEN_RE.finditer(text):
                word, ws = m.group(1), m.group(2)
                tag = "NN"
                if word in ".,;:!?—…\"'()[]":
                    tag = word if word in ".,:" else "."
                elif word.isdigit():
                    tag = "CD"
                out.append(_SpanToken(text=word, tag_=tag, whitespace_=ws))
            return out

    util_mod = types.ModuleType("spacy.util")
    util_mod.is_package = lambda name: True
    cli_mod = types.ModuleType("spacy.cli")
    cli_mod.download = lambda name: None
    spacy_mod.util = util_mod
    spacy_mod.cli = cli_mod
    spacy_mod.load = lambda name: _DummyNLP()
    sys.modules["spacy"] = spacy_mod
    sys.modules["spacy.util"] = util_mod
    sys.modules["spacy.cli"] = cli_mod

_PIPELINE = None


def get_pipeline():
    """Lazily initializes the Kokoro TTS pipeline."""
    global _PIPELINE
    if _PIPELINE is None:
        try:
            import espeakng_loader
            from phonemizer.backend.espeak.wrapper import EspeakWrapper

            EspeakWrapper.set_library(espeakng_loader.get_library_path())
            if hasattr(EspeakWrapper, "set_data_path"):
                EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
            else:
                os.environ["PHONEMIZER_ESPEAK_DATA"] = espeakng_loader.get_data_path()
        except Exception as exc:
            logger.warning(f"Could not initialize espeakng: {exc}")

        from kokoro import KPipeline

        _PIPELINE = KPipeline(lang_code="a", device="cpu")
    return _PIPELINE


def synthesize_speech(text: str, voice_id: str = "af_heart", speed: float = 1.0) -> Any:
    """Synthesizes voice audio and wraps into ManimGX Speech object."""
    import numpy as np
    from manimgx import Speech

    pipe = get_pipeline()
    chunks: list[np.ndarray] = []
    for _, _, audio in pipe(text, voice=voice_id, speed=speed):
        if audio is not None:
            arr = audio.detach().cpu().numpy().astype(np.float32)
            chunks.append(arr)

    if not chunks:
        samples = np.zeros(24000, dtype=np.float32)
    else:
        samples = np.concatenate(chunks)

    return Speech(samples, text=text, rate=24000)
