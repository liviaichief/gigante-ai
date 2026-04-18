import logging
import sys
from pathlib import Path

from fastapi import FastAPI

from app.webhook import router as webhook_router
from config.settings import PORT

# ── Logging ──────────────────────────────────────────────────────────────────
Path("data/logs").mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data/logs/app.log", encoding="utf-8"),
    ],
)

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="Mentor AN", version="0.1.0", docs_url="/docs")
app.include_router(webhook_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Mentor AN"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
