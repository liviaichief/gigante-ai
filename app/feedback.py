import asyncio
from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from db.client import insert_chunks
from config.settings import OPENAI_API_KEY

router = APIRouter()
_openai = OpenAI(api_key=OPENAI_API_KEY)


class FeedbackRequest(BaseModel):
    session_id: str
    message: str
    response: str
    rating: int  # 1 = like, -1 = dislike


@router.post("/api/feedback")
async def receive_feedback(req: FeedbackRequest):
    if req.rating == 1:
        # Auto-learning: embed the approved Q&A and add to RAG knowledge base
        text = (
            f"Pergunta: {req.message}\n\n"
            f"Resposta aprovada pelo usuário:\n{req.response}"
        )

        def _embed_and_store():
            emb = _openai.embeddings.create(
                model="text-embedding-3-small",
                input=[text],
            )
            vec = emb.data[0].embedding
            insert_chunks([{
                "content": text,
                "embedding": vec,
                "source": "aprendizado_usuario",
                "title": "Aprendizado — Feedback Positivo",
                "chunk_index": 0,
            }])

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _embed_and_store)

    return {"status": "ok"}
