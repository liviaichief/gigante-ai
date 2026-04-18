"""
Fetch and clean YouTube transcripts.
Supports: youtube.com/watch?v=ID, youtu.be/ID, youtube.com/shorts/ID
"""
import re
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled


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
    Returns {"video_id", "title", "content"} or raises ValueError.
    Tries Portuguese first, then English, then any available language.
    """
    video_id = _extract_video_id(url)
    if not video_id:
        raise ValueError(f"Could not extract video ID from URL: {url}")

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Priority: pt-BR > pt > en > any
        transcript = None
        for lang in ["pt-BR", "pt", "en"]:
            try:
                transcript = transcript_list.find_transcript([lang])
                break
            except Exception:
                continue

        if transcript is None:
            transcript = transcript_list.find_generated_transcript(
                [t.language_code for t in transcript_list]
            )

        entries = transcript.fetch()
        text = " ".join(entry["text"] for entry in entries)
        text = re.sub(r"\s+", " ", text).strip()

        return {
            "video_id": video_id,
            "title": f"YouTube {video_id}",
            "content": text,
            "source": f"youtube_{video_id}.txt",
            "url": url,
        }

    except (NoTranscriptFound, TranscriptsDisabled) as e:
        raise ValueError(f"No transcript available for {video_id}: {e}")
