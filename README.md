# Veraxi-ManimGX 🛡️🎬

**Grounded Forensic Video Production Pipeline bridging Veraxi GraphRAG with ManimGX.**

`veraxi-manimgx` is an automated documentary and explainer engine that transforms forensic accounting and legal literature into 3Blue1Brown-style programmatic video animations. Every claim spoken in the video is mathematically audited against indexed primary sources (SEC 10-Ks, forensic books, court transcripts) before rendering.

---

## 🏛️ Hybrid System Architecture

`veraxi-manimgx` employs a **Two-Tier Hybrid Grounding Architecture**:
1. **Host AI Semantic Evaluation:** Frontier intelligence understands accounting nuances, allows natural voiceover paraphrasing, and catches subtle polarity reversals (e.g., false negations).
2. **Deterministic Citation Anchor:** Validates that every spoken claim is tethered to a non-empty, verbatim primary source quote and real page number from Veraxi's Neo4j/Qdrant index.

```text
User Topic ("Allied Capital PIK Shenanigans")
                     │
         ┌───────────▼───────────┐
         │ 1. Veraxi MCP Client  │  Hybrid Search (Neo4j Graph + Qdrant Vectors)
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
                     │  Blocks unanchored or inverted claims
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
| **`veraxi_manimgx.client`** | Asynchronous MCP client calling `api.veraxi.me/mcp` for `mcp_merge_rank`, `mcp_query_graph`, and `mcp_fact_check`. |
| **`veraxi_manimgx.core.models`** | Pydantic data schemas: `Storyboard`, `ScriptBeat`, `EvidenceCitation`, `EntityRelation`. |
| **`veraxi_manimgx.core.fact_gate`** | Grounding verification gate ensuring zero ungrounded assertions reach the video renderer. |
| **`veraxi_manimgx.templates`** | High-production Manim visual components: `ProofCard` (3D floating evidence exhibits) and `EntityNetwork` (Neo4j multi-hop paths). |
| **`veraxi_manimgx.generators`** | Transpiles verified storyboards into executable ManimGX scene scripts (`self.say()`). |
| **`veraxi_manimgx.voice`** | Kokoro-82M neural TTS wrapper with word-level animation bracket sync. |

---

## 🚀 Quickstart

### 1. Installation

```bash
git clone https://github.com/kcoaguila-dev/veraxi-manimgx.git
cd veraxi-manimgx
pip install -e .
```

To install optional animation and TTS dependencies:
```bash
pip install -e ".[animation]"
```

### 2. Verify Database Connection

```bash
python -m veraxi_manimgx.cli stats
```

### 3. Generate a Fact-Checked Manim Scene

```bash
python -m veraxi_manimgx.cli generate "David Einhorn Allied Capital PIK interest" --output scene.py
```

### 4. Render with ManimGX

```bash
manimgx render scene.py -o AlliedCapitalPIK.mp4
```

---

## 🧪 Testing

Run automated unit and integration tests:

```bash
pytest tests/ -v
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
