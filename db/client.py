"""
Supabase client via direct HTTP (PostgREST + RPC).
Avoids the supabase-py SDK and its heavy dependency chain.
"""
import httpx
from config.settings import SUPABASE_URL, SUPABASE_SERVICE_KEY

_HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}


def _rest(path: str) -> str:
    return f"{SUPABASE_URL}/rest/v1{path}"


# ── Sync client (used in ingest pipeline) ────────────────────────────────────

def insert_chunks(rows: list[dict]) -> None:
    with httpx.Client(timeout=30) as client:
        resp = client.post(_rest("/chunks"), json=rows, headers=_HEADERS)
        resp.raise_for_status()


def delete_all_chunks() -> None:
    with httpx.Client(timeout=30) as client:
        resp = client.delete(
            _rest("/chunks"),
            params={"id": "neq.00000000-0000-0000-0000-000000000000"},
            headers=_HEADERS,
        )
        resp.raise_for_status()


def delete_chunks_by_source(source: str) -> None:
    with httpx.Client(timeout=30) as client:
        resp = client.delete(
            _rest("/chunks"),
            params={"source": f"eq.{source}"},
            headers=_HEADERS,
        )
        resp.raise_for_status()


def get_all_sources() -> list[dict]:
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            _rest("/chunks"),
            params={"select": "source,title,chunk_index", "order": "title.asc"},
            headers=_HEADERS,
        )
        resp.raise_for_status()
        rows = resp.json()

    # Group by source, count chunks
    seen: dict[str, dict] = {}
    for row in rows:
        s = row["source"]
        if s not in seen:
            seen[s] = {"source": s, "title": row["title"], "chunks": 0}
        seen[s]["chunks"] += 1
    return list(seen.values())


def rpc_match_chunks(query_embedding: list[float], match_count: int, min_score: float) -> list[dict]:
    with httpx.Client(timeout=30) as client:
        resp = client.post(
            _rest("/rpc/match_chunks"),
            json={
                "query_embedding": query_embedding,
                "match_count": match_count,
                "min_score": min_score,
            },
            headers=_HEADERS,
        )
        resp.raise_for_status()
        return resp.json()


# ── Async client (used in FastAPI webhook) ───────────────────────────────────

async def async_insert_session(rows: list[dict]) -> None:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(_rest("/sessions"), json=rows, headers=_HEADERS)
        resp.raise_for_status()


async def async_get_history(phone: str, limit: int) -> list[dict]:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            _rest("/sessions"),
            params={
                "phone": f"eq.{phone}",
                "order": "created_at.desc",
                "limit": limit,
                "select": "role,content",
            },
            headers=_HEADERS,
        )
        resp.raise_for_status()
        return resp.json()


async def async_count_sessions(phone: str) -> int:
    headers = {**_HEADERS, "Prefer": "count=exact"}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            _rest("/sessions"),
            params={"phone": f"eq.{phone}", "limit": 1},
            headers=headers,
        )
        resp.raise_for_status()
        content_range = resp.headers.get("content-range", "0")
        try:
            return int(content_range.split("/")[-1])
        except ValueError:
            return 0


async def async_insert_log(row: dict) -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(_rest("/conversation_logs"), json=row, headers=_HEADERS)
        resp.raise_for_status()
