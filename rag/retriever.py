from openai import OpenAI
from db.client import get_client
from config.settings import TOP_K, MIN_SCORE, OPENAI_API_KEY

_openai = OpenAI(api_key=OPENAI_API_KEY)


def search(query: str, top_k: int = TOP_K) -> list[dict]:
    """Return top-k chunks above MIN_SCORE for the given query."""
    embedding_resp = _openai.embeddings.create(
        model="text-embedding-3-small",
        input=[query],
    )
    query_vec = embedding_resp.data[0].embedding

    db = get_client()
    result = db.rpc(
        "match_chunks",
        {
            "query_embedding": query_vec,
            "match_count": top_k,
            "min_score": MIN_SCORE,
        },
    ).execute()

    return [
        {
            "content": row["content"],
            "source": row.get("title") or row.get("source") or "Desconhecido",
            "score": round(row["score"], 3),
        }
        for row in (result.data or [])
    ]
