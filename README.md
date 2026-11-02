# Veraxi-ManimGX 🛡️🎬

**Grounded Forensic & Quantitative Video Production Pipeline bridging Veraxi GraphRAG with ManimGX.**

`veraxi-manimgx` is an automated documentary and explainer engine that transforms forensic accounting literature, SEC filings, and live web research into 3Blue1Brown-style programmatic video animations. Every claim spoken by the narrator is audited against primary sources before rendering to guarantee zero factual hallucination.

---

## 🏛️ Hybrid System Architecture

`veraxi-manimgx` employs a **Two-Tier Hybrid Grounding Architecture** that combines the strengths of frontier semantic reasoning and deterministic verification:

1. **Host AI Semantic Evaluation:** Frontier intelligence understands accounting mechanisms, allows natural voiceover paraphrasing, and catches polarity reversals (such as subtle negation traps).
2. **Deterministic Citation Anchor:** Validates that every spoken beat is anchored to a non-empty, verbatim primary source quote, document source, and exact page number from Veraxi's Neo4j / Qdrant index.

```text
User Topic / URL ("Allied Capital PIK Shenanigans")
                     │
         ┌───────────▼───────────┐
         │ 1. Veraxi MCP Client  │  Hybrid Search (Neo4j Graph + Qdrant Vectors)
         │                       │  or Ephemeral Web RAG (on-the-fly URL crawl)
         └───────────┬───────────┘
                     │  Extracts verbatim proof quotes, page numbers, entity edges
         ┌───────────▼───────────┐
         │ 2. Host AI Author 🧠  │  Translates accounting mechanisms into natural voiceover
         │                       │  Embeds bracketed [anim] markers for ManimGX
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │ 3. Hybrid Fact Gate 🛡│  Tier 1: Host AI confirms faithful semantic meaning
         │                       │  Tier 2: Deterministic engine anchors quote & page
         └───────────┬───────────┘
                     │  Blocks unanchored, inverted, or fabricated claims
         ┌───────────▼───────────┐
         │ 4. ManimGX Generator  │  Compiles verified beats into self.say() code
         └───────────┬───────────┘
                     │  Attaches ProofCard & EntityNetwork visual components
         ┌───────────▼───────────┐
         │ 5. Kokoro-82M + Manim │  Synthesizes speech and renders 60fps MP4
         └───────────────────────┘
```

---

## 📦 Core Modules

| Module | Purpose |
| :--- | :--- |
| **`veraxi_manimgx.client`** | Asynchronous MCP client connecting to `api.veraxi.me/mcp` for `mcp_merge_rank`, `mcp_query_graph`, `mcp_fact_check`, `mcp_ephemeral_web_rag`, and `mcp_ingest_document`. |
| **`veraxi_manimgx.core.models`** | Pydantic data schemas: `Storyboard`, `ScriptBeat`, `EvidenceCitation`, `EntityRelation`, `EvaluationStrategy`. |
| **`veraxi_manimgx.core.fact_gate`** | Hybrid Grounding Gate combining Host AI semantic checks with deterministic citation anchor validation. |
| **`veraxi_manimgx.templates`** | High-production Manim visual components: `ProofCard` (3D floating evidence exhibits) and `EntityNetwork` (Neo4j multi-hop paths). |
| **`veraxi_manimgx.generators`** | Transpiles verified storyboards into executable ManimGX scene scripts using `self.say()`. |
| **`veraxi_manimgx.voice`** | Kokoro-82M neural TTS wrapper with word-bracket animation synchronization. |
| **`veraxi_manimgx.pipeline`** | End-to-end production orchestrator: Research $\rightarrow$ Fact Gate $\rightarrow$ ManimGX Compilation. |

---

## 🚀 Quickstart

### 1. Installation

```bash
git clone https://github.com/kcoaguila-dev/veraxi-manimgx.git
cd veraxi-manimgx
pip install -e .
```

To install optional animation and neural voice dependencies:
```bash
pip install -e ".[animation]"
```

### 2. Verify Database Connection

```bash
python -m veraxi_manimgx.cli stats
```

---

## 🎬 Production Workflows

### Workflow A: Generate from Pre-Indexed Literature
Produce a fact-checked video based on indexed books (*Financial Shenanigans*, *Fooling Some of the People All of the Time*):

```bash
python -m veraxi_manimgx.cli generate "David Einhorn Allied Capital PIK interest" --output scene.py --beats 3
```

### Workflow B: Generate from External Web URLs (Ephemeral Web RAG)
Produce a video on fresh topics not yet in the database by passing external URLs on-the-fly:

```bash
python -m veraxi_manimgx.cli generate "Enron mark to market accounting fraud" \
  --url "https://en.wikipedia.org/wiki/Enron_scandal" \
  --output enron_scene.py
```

### Workflow C: Permanent Knowledge Ingestion
Permanently add SEC 10-K filings, annual reports, or court transcripts into the Neo4j graph and Qdrant index:

```python
from veraxi_manimgx.client.veraxi_client import VeraxiClient

client = VeraxiClient()
await client.ingest_document(
    url="https://www.sec.gov/Archives/edgar/data/...",
    wait_for_completion=True
)
```

---

## 🎥 Rendering with ManimGX

Once your scene file is generated, render it in 1080p / 60fps with speech audio and synchronized captions:

```bash
manimgx render scene.py -o ForensicExplainer.mp4
```

* **Speech Synthesis:** Kokoro-82M generates character voices for each line.
* **Animation Sync:** Visual components (`ProofCard`, `EntityNetwork`) animate at the exact millisecond bracketed words are spoken.
* **Captions:** Timed `.srt` subtitles are automatically exported.

---

## 🧪 Testing

Run the automated test suite covering Storyboards, Code Generation, Fact Gates, and Negation Polarity Checks:

```bash
pytest tests/ -v
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
