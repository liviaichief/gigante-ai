import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config.settings import ADMIN_TOKEN
from ingest.chunker import chunk_text
from ingest.embedder import generate_embeddings
from ingest.youtube import fetch_transcript
from db.client import insert_chunks, delete_chunks_by_source, get_all_sources

router = APIRouter(prefix="/admin")
log = logging.getLogger(__name__)

_STATIC = Path(__file__).parent / "static"


@router.get("")
async def admin_page():
    return FileResponse(str(_STATIC / "admin.html"))


def _auth(token: str | None) -> None:
    if not token or token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


class TextPayload(BaseModel):
    title: str
    content: str


class YoutubePayload(BaseModel):
    url: str
    title: str = ""


class DeletePayload(BaseModel):
    source: str


def _index_document(title: str, content: str, source: str) -> int:
    """Chunk, embed and store a document. Returns chunk count."""
    chunks = chunk_text(content)
    if not chunks:
        raise ValueError("Content too short to index.")

    embeddings = generate_embeddings(chunks)
    rows = [
        {
            "content": text,
            "embedding": emb,
            "source": source,
            "title": title,
            "chunk_index": i,
        }
        for i, (text, emb) in enumerate(zip(chunks, embeddings))
    ]
    insert_chunks(rows)
    return len(chunks)


@router.post("/ingest/text")
async def ingest_text(
    payload: TextPayload,
    x_admin_token: str | None = Header(default=None),
):
    _auth(x_admin_token)

    source = payload.title.lower().replace(" ", "_")[:50] + ".txt"
    delete_chunks_by_source(source)

    count = _index_document(payload.title, payload.content, source)
    log.info("Indexed text '%s': %d chunks", payload.title, count)
    return {"status": "ok", "source": source, "chunks": count}


@router.post("/ingest/youtube")
async def ingest_youtube(
    payload: YoutubePayload,
    x_admin_token: str | None = Header(default=None),
):
    _auth(x_admin_token)

    try:
        doc = fetch_transcript(payload.url)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if payload.title:
        doc["title"] = payload.title

    delete_chunks_by_source(doc["source"])
    count = _index_document(doc["title"], doc["content"], doc["source"])

    log.info("Indexed YouTube '%s': %d chunks", doc["title"], count)
    return {"status": "ok", "source": doc["source"], "chunks": count, "title": doc["title"]}


@router.delete("/source")
async def delete_source(
    payload: DeletePayload,
    x_admin_token: str | None = Header(default=None),
):
    _auth(x_admin_token)
    delete_chunks_by_source(payload.source)
    return {"status": "ok", "deleted": payload.source}


@router.get("/sources")
async def list_sources(x_admin_token: str | None = Header(default=None)):
    _auth(x_admin_token)
    sources = get_all_sources()
    return {"sources": sources}
