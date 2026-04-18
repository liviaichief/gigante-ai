from fastapi import APIRouter
from pydantic import BaseModel

from app.session import get_history, add
from config.persona import FALLBACK_MESSAGE
from rag.retriever import search
from rag.prompt_builder import build_prompt
from rag.llm_client import ask

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str


@router.post("/api/chat")
async def chat(req: ChatRequest):
    chunks = search(req.message)

    if not chunks:
        response_text = FALLBACK_MESSAGE
    else:
        history = await get_history(req.session_id)
        system, question = build_prompt(req.message, chunks, history)
        response_text = ask(system, question)

    await add(req.session_id, req.message, response_text)
    return {"response": response_text}
