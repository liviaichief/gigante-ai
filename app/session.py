from db.client import async_count_sessions, async_get_history, async_insert_session
from config.settings import MAX_HISTORY


async def is_new(phone: str) -> bool:
    count = await async_count_sessions(phone)
    return count == 0


async def get_history(phone: str) -> list[dict]:
    rows = await async_get_history(phone, limit=MAX_HISTORY * 2)
    rows = list(reversed(rows))

    history: list[dict] = []
    i = 0
    while i < len(rows) - 1:
        if rows[i]["role"] == "user" and rows[i + 1]["role"] == "assistant":
            history.append({"user": rows[i]["content"], "assistant": rows[i + 1]["content"]})
            i += 2
        else:
            i += 1
    return history


async def add(phone: str, user_msg: str, assistant_msg: str) -> None:
    await async_insert_session([
        {"phone": phone, "role": "user",      "content": user_msg},
        {"phone": phone, "role": "assistant", "content": assistant_msg},
    ])
