import httpx
from config.settings import ZAPI_INSTANCE, ZAPI_TOKEN, ZAPI_CLIENT_TOKEN

_BASE = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}"
_HEADERS = {"Client-Token": ZAPI_CLIENT_TOKEN, "Content-Type": "application/json"}


async def send_text(phone: str, text: str) -> dict:
    """Send a plain-text WhatsApp message via Z-API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{_BASE}/send-text",
            json={"phone": phone, "message": text},
            headers=_HEADERS,
        )
        resp.raise_for_status()
        return resp.json()
