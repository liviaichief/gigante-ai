"""
Run with:  python -m ingest.pipeline
"""
from ingest.loader import load_transcripts
from ingest.chunker import chunk_text
from ingest.embedder import generate_embeddings
from db.client import insert_chunks, delete_all_chunks

BATCH_SIZE = 50


def run_ingestion(reset: bool = True) -> None:
    print("\n=== Mentor AN — Ingestion Pipeline ===\n")

    if reset:
        delete_all_chunks()
        print("Chunks anteriores removidos.\n")

    documents = load_transcripts()
    if not documents:
        print("⚠️  Nenhum .txt em data/transcripts/")
        return

    total_chunks = 0

    for doc in documents:
        chunks = chunk_text(doc["content"])
        print(f"  + {doc['source']}: {len(chunks)} chunks")

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
            insert_chunks(rows)

        total_chunks += len(chunks)

    print(f"\n✅ Concluído: {len(documents)} arquivo(s), {total_chunks} chunks indexados.\n")


if __name__ == "__main__":
    run_ingestion()
