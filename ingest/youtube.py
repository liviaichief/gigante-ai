"""
Fetch YouTube transcripts using youtube-transcript-api >= 0.6.x
"""
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled

_api = YouTubeTranscriptApi()


def _extract_video_id(url: str) -> str | None:
    patterns = [
        r"(?:v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:shorts/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_transcript(url: str) -> dict:
    """
    Returns {"video_id", "title", "content", "source", "url"} or raises ValueError.
    Tries pt-BR > pt > en > any available language.
    """
    video_id = _extract_video_id(url)
    if not video_id:
        raise ValueError(f"Não foi possível extrair o ID do vídeo: {url}")

    try:
        # Try preferred languages first
        entries = None
        for langs in [["pt-BR", "pt"], ["en"], None]:
            try:
                if langs:
                    entries = _api.fetch(video_id, languages=langs)
                else:
                    # Fallback: list available and pick first
                    available = _api.list(video_id)
                    first = next(iter(available), None)
                    if first:
                        entries = _api.fetch(video_id, languages=[first.language_code])
                break
            except (NoTranscriptFound, Exception):
                continue

        if not entries:
            raise ValueError("Nenhuma transcrição disponível para este vídeo.")

        text = " ".join(e.text for e in entries)
        text = re.sub(r"\s+", " ", text).strip()

        if len(text) < 100:
            raise ValueError("Transcrição muito curta ou vazia.")

        return {
            "video_id": video_id,
            "title": f"YouTube {video_id}",
            "content": text,
            "source": f"youtube_{video_id}.txt",
            "url": url,
        }

    except (TranscriptsDisabled, Exception) as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Erro ao buscar transcrição: {str(e)}")
