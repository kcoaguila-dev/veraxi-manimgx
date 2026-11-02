"""Asynchronous client for interacting with Veraxi MCP server."""

from __future__ import annotations

import json
import logging
import os
from typing import Any
import httpx

from veraxi_manimgx.core.models import (
    EvidenceCitation,
    FactCheckVerdict,
    EntityRelation,
)

logger = logging.getLogger(__name__)

DEFAULT_MCP_URL = "https://api.veraxi.me/mcp"
DEFAULT_TOKEN = "vx-4eee982f536f4be10fe8bdbce2a3b91dc88c3eb226ebc8b2a66bedf2a16b89aa"


class VeraxiClient:
    """Connects to the Veraxi GraphRAG & Fact-Check Proof Engine via MCP JSON-RPC."""

    def __init__(
        self,
        base_url: str | None = None,
        bearer_token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url or os.environ.get("VERAXI_MCP_URL", DEFAULT_MCP_URL)
        self.token = bearer_token or os.environ.get("VERAXI_API_KEY", DEFAULT_TOKEN)
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Invokes an MCP tool on the Veraxi server."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.base_url,
                json=payload,
                headers=self._headers(),
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise RuntimeError(f"Veraxi MCP Error: {data['error']}")

            result = data.get("result", {})
            content = result.get("content", [])
            if content and isinstance(content, list):
                # Returns the text payload of the tool output
                return content[0].get("text", "")
            return result

    async def get_stats(self) -> dict[str, Any]:
        """Fetches Neo4j and Qdrant database statistics."""
        raw = await self.call_tool("mcp_get_database_stats", {})
        try:
            return json.loads(raw)
        except Exception:
            return {"raw": raw}

    async def hybrid_search(
        self, query: str, limit: int = 5, entity_name: str = "", max_hops: int = 2
    ) -> list[EvidenceCitation]:
        """Hybrid vector and graph RRF search across forensic accounting index."""
        raw = await self.call_tool(
            "mcp_merge_rank",
            {
                "query_text": query,
                "limit": limit,
                "entity_name": entity_name,
                "max_hops": max_hops,
            },
        )
        return self._extract_citations_from_mcp_output(raw)

    async def query_entity_graph(
        self, entity_name: str, max_hops: int = 2
    ) -> list[EntityRelation]:
        """Traverses entity connections and money flows in Neo4j."""
        raw = await self.call_tool(
            "mcp_query_graph",
            {"entity_name": entity_name, "max_hops": max_hops},
        )
        # Parses JSON relations from the raw tool response
        relations: list[EntityRelation] = []
        try:
            if "```json" in raw:
                json_part = raw.split("```json")[1].split("```")[0].strip()
                data = json.loads(json_part)
                for item in data:
                    payload = item.get("payload", {})
                    src = payload.get("source_entity") or entity_name
                    tgt = payload.get("target_entity") or payload.get("name", "Unknown")
                    rel = payload.get("relation") or payload.get("type", "RELATED_TO")
                    relations.append(
                        EntityRelation(
                            source_entity=src,
                            target_entity=tgt,
                            relation_type=rel,
                            properties=payload,
                        )
                    )
        except Exception as exc:
            logger.debug(f"Failed to parse graph relations: {exc}")
        return relations

    async def fact_check(self, claim: str, min_score: float = 0.8) -> FactCheckVerdict:
        """Verifies a script claim against literature and returns proof quotes."""
        raw = await self.call_tool(
            "mcp_fact_check",
            {"claim": claim, "min_score": min_score},
        )
        passed = "FACT CHECK PASSED" in raw
        citations = self._extract_citations_from_mcp_output(raw)

        # Extract score if formatted
        score = 1.0 if passed else 0.0
        if "Grounding Score:** `" in raw:
            try:
                score_str = raw.split("Grounding Score:** `")[1].split("`")[0]
                score = float(score_str)
            except Exception:
                pass

        return FactCheckVerdict(
            claim=claim,
            passed=passed,
            score=score,
            threshold=min_score,
            citations=citations,
            verdict_text=raw,
        )

    def _extract_citations_from_mcp_output(self, text: str) -> list[EvidenceCitation]:
        citations = []
        try:
            if "```json" in text:
                json_part = text.split("```json")[1].split("```")[0].strip()
                hits = json.loads(json_part)
                for h in hits:
                    payload = h.get("payload", {})
                    citations.append(
                        EvidenceCitation(
                            id=str(h.get("id")),
                            source=payload.get("source")
                            or payload.get("document_id")
                            or "Document",
                            page=payload.get("page_number"),
                            breadcrumb=payload.get("breadcrumb"),
                            verbatim_quote=payload.get("text", "")[:300],
                            chunk_text=payload.get("text", ""),
                            score=h.get("score") or h.get("fused_score"),
                        )
                    )
        except Exception:
            pass
        return citations
