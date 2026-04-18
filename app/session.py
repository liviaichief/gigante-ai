from db.client import get_client
from config.settings import MAX_HISTORY


def is_new(phone: str) -> bool:
    db = get_client()
    result = (
        db.table("sessions")
        .select("id", count="exact")
        .eq("phone", phone)
        .limit(1)
        .execute()
    )
    return result.count == 0


def get_history(phone: str) -> list[dict]:
    """Return last MAX_HISTORY * 2 messages as [{user, assistant}] pairs."""
    db = get_client()
    result = (
        db.table("sessions")
        .select("role, content")
        .eq("phone", phone)
        .order("created_at", desc=True)
        .limit(MAX_HISTORY * 2)
        .execute()
    )

    rows = list(reversed(result.data or []))

    # Pair user+assistant turns
    history: list[dict] = []
    i = 0
    while i < len(rows) - 1:
        if rows[i]["role"] == "user" and rows[i + 1]["role"] == "assistant":
            history.append({"user": rows[i]["content"], "assistant": rows[i + 1]["content"]})
            i += 2
        else:
            i += 1

    return history


def add(phone: str, user_msg: str, assistant_msg: str) -> None:
    db = get_client()
    db.table("sessions").insert([
        {"phone": phone, "role": "user",      "content": user_msg},
        {"phone": phone, "role": "assistant", "content": assistant_msg},
    ]).execute()
