from pathlib import Path


def load_transcripts(folder: str = "data/transcripts") -> list[dict]:
    """Load all .txt files from the transcripts folder."""
    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)

    documents = []
    for file_path in sorted(folder_path.glob("*.txt")):
        content = file_path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        documents.append({
            "content": content,
            "source": file_path.name,
            "title": file_path.stem.replace("_", " ").replace("-", " ").title(),
        })
        print(f"  Loaded: {file_path.name} ({len(content):,} chars)")

    return documents
