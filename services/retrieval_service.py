"""
services/retrieval_service.py

CRITICAL:
  - DO NOT recreate or reindex the Qdrant collection.
  - Only perform READ (search) operations on the existing collection.
  - Returns empty list immediately if QDRANT_ENABLED=false (default).
"""

import logging
from typing import List, Dict, Any, Optional

from config import settings

logger = logging.getLogger(__name__)

_qdrant_client = None


def _get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is None:
        try:
            from qdrant_client import AsyncQdrantClient
            _qdrant_client = AsyncQdrantClient(url=settings.qdrant_url)
        except ImportError:
            logger.warning("qdrant-client not installed. Retrieval disabled.")
    return _qdrant_client


async def retrieve_relevant_context(
    query: str, top_k: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Runs similarity search on an existing Qdrant collection (READ-ONLY).
    Returns empty list immediately if QDRANT_ENABLED=false (default).
    """
    # Short-circuit if retrieval is disabled — avoids slow HTTP timeouts
    if not settings.qdrant_enabled:
        return []

    client = _get_qdrant_client()
    if client is None:
        return []

    k = top_k or settings.qdrant_top_k

    try:
        from clients.sarvam_client import embed_text
        query_vector = await embed_text(query)

        results = await client.search(
            collection_name=settings.qdrant_collection,
            query_vector=query_vector,
            limit=k,
            with_payload=True,
        )

        chunks = []
        for hit in results:
            payload = hit.payload or {}
            chunks.append({
                "text": payload.get("text", payload.get("content", str(payload))),
                "score": round(hit.score, 4),
                "metadata": {k: v for k, v in payload.items() if k not in ("text", "content")},
            })
        return chunks

    except Exception as exc:
        logger.warning(f"Qdrant retrieval skipped: {exc}")
        return []
