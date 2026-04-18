from openai import OpenAI
from db.client import rpc_match_chunks
from config.settings import TOP_K, MIN_SCORE, OPENAI_API_KEY

_openai = OpenAI(api_key=OPENAI_API_KEY)


def search(query: str, top_k: int = TOP_K) -> list[dict]:
    embedding_resp = _openai.embeddings.create(
        model="text-embedding-3-small",
        input=[query],
    )
    query_vec = embedding_resp.data[0].embedding

    rows = rpc_match_chunks(query_vec, top_k, MIN_SCORE)

    return [
        {
            "content": row["content"],
            "source": row.get("title") or row.get("source") or "Desconhecido",
            "score": round(row["score"], 3),
        }
        for row in (rows or [])
    ]
