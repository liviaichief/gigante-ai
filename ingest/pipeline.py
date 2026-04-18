"""
Run with:  python -m ingest.pipeline
Indexes all .txt files from data/transcripts/ into Supabase pgvector.
"""
from ingest.loader import load_transcripts
from ingest.chunker import chunk_text
from ingest.embedder import generate_embeddings
from db.client import get_client

BATCH_SIZE = 50


def run_ingestion(reset: bool = True) -> None:
    print("\n=== Mentor AN — Ingestion Pipeline (Supabase) ===\n")

    db = get_client()

    if reset:
        db.table("chunks").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("Cleared existing chunks.\n")

    documents = load_transcripts()
    if not documents:
        print("⚠️  No .txt files found in data/transcripts/")
        print("Add your transcript files and run again.\n")
        return

    total_chunks = 0

    for doc in documents:
        chunks = chunk_text(doc["content"])
        print(f"  → {doc['source']}: {len(chunks)} chunks")

        for batch_start in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[batch_start : batch_start + BATCH_SIZE]
            embeddings = generate_embeddings(batch)

            rows = [
                {
                    "content": text,
                    "embedding": embedding,
                    "source": doc["source"],
                    "title": doc["title"],
                    "chunk_index": batch_start + j,
                }
                for j, (text, embedding) in enumerate(zip(batch, embeddings))
            ]

            db.table("chunks").insert(rows).execute()

        total_chunks += len(chunks)

    print(f"\n✅ Done: {len(documents)} file(s), {total_chunks} chunks indexed.\n")


if __name__ == "__main__":
    run_ingestion()
