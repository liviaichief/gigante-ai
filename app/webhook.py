import logging
import time

from fastapi import APIRouter, Request, HTTPException

from app import session
from app.whatsapp import send_text
from config.persona import FALLBACK_MESSAGE, WELCOME_MESSAGE
from db.client import async_insert_log
from rag.retriever import search
from rag.prompt_builder import build_prompt
from rag.llm_client import ask

router = APIRouter()
log = logging.getLogger(__name__)


def _parse_zapi(payload: dict) -> tuple[str, str] | None:
    try:
        phone = payload["phone"]
        text = payload.get("text", {}).get("message", "").strip()
        if payload.get("fromMe") or not text:
            return None
        return phone, text
    except (KeyError, TypeError):
        return None


def _parse_evolution(payload: dict) -> tuple[str, str] | None:
    try:
        data = payload["data"]
        if data["key"]["fromMe"]:
            return None
        phone = data["key"]["remoteJid"].replace("@s.whatsapp.net", "")
        text = (data.get("message") or {}).get("conversation", "").strip()
        if not text:
            return None
        return phone, text
    except (KeyError, TypeError):
        return None


@router.post("/webhook")
async def webhook(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    parsed = _parse_zapi(payload) or _parse_evolution(payload)
    if parsed is None:
        return {"status": "ignored"}

    phone, message = parsed
    t0 = time.monotonic()

    if await session.is_new(phone):
        await send_text(phone, WELCOME_MESSAGE)

    chunks = search(message)

    if not chunks:
        response_text = FALLBACK_MESSAGE
    else:
        history = await session.get_history(phone)
        system, question = build_prompt(message, chunks, history)
        response_text = ask(system, question)

    await send_text(phone, response_text)
    await session.add(phone, message, response_text)

    latency_ms = round((time.monotonic() - t0) * 1000)

    try:
        await async_insert_log({
            "phone_suffix": phone[-4:],
            "question": message[:500],
            "sources": [c["source"] for c in chunks],
            "had_fallback": not chunks,
            "latency_ms": latency_ms,
        })
    except Exception:
        pass

    log.info("handled phone=...%s fallback=%s latency_ms=%d", phone[-4:], not chunks, latency_ms)
    return {"status": "ok"}
