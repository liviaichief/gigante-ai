from openai import OpenAI
from config.settings import OPENAI_API_KEY

_client = OpenAI(api_key=OPENAI_API_KEY)
EMBED_MODEL = "text-embedding-3-small"


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts (batched)."""
    response = _client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in response.data]
