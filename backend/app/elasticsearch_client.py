"""Elasticsearch async client and index management helpers."""

import logging
from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Singleton client — initialized on startup via lifespan
_es_client: AsyncElasticsearch | None = None

VULNERABILITY_INDEX_MAPPING: dict[str, Any] = {
    "mappings": {
        "properties": {
            "cve_id": {"type": "keyword"},
            "description": {"type": "text", "analyzer": "english"},
            "severity": {"type": "keyword"},
            "cvss_score": {"type": "float"},
            "epss_score": {"type": "float"},
            "published_date": {"type": "date"},
            "modified_date": {"type": "date"},
            "source": {"type": "keyword"},
            "exploit_available": {"type": "boolean"},
            "cisa_kev": {"type": "boolean"},
            "affected_products": {"type": "text"},
        }
    }
}


def get_es_client() -> AsyncElasticsearch:
    """Return the shared Elasticsearch client instance."""
    if _es_client is None:
        raise RuntimeError("Elasticsearch client not initialized. Call init_es() first.")
    return _es_client


async def init_es() -> AsyncElasticsearch:
    """Initialize the Elasticsearch client and ensure required indices exist."""
    global _es_client  # noqa: PLW0603
    _es_client = AsyncElasticsearch(
        settings.elasticsearch_url,
        request_timeout=30,
        retry_on_timeout=True,
        max_retries=3,
    )
    await ensure_index(
        _es_client,
        settings.elasticsearch_index_vulnerabilities,
        VULNERABILITY_INDEX_MAPPING,
    )
    logger.info("Elasticsearch client initialized at %s", settings.elasticsearch_url)
    return _es_client


async def close_es() -> None:
    """Close the Elasticsearch client gracefully."""
    global _es_client  # noqa: PLW0603
    if _es_client is not None:
        await _es_client.close()
        _es_client = None


async def ensure_index(
    client: AsyncElasticsearch, index_name: str, mapping: dict[str, Any]
) -> None:
    """Create index with mapping if it does not already exist."""
    try:
        exists = await client.indices.exists(index=index_name)
        if not exists:
            await client.indices.create(index=index_name, body=mapping)
            logger.info("Created Elasticsearch index: %s", index_name)
    except NotFoundError:
        await client.indices.create(index=index_name, body=mapping)
    except Exception as exc:
        logger.warning("Could not ensure ES index '%s': %s", index_name, exc)
