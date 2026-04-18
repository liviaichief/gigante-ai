import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.webhook import router as webhook_router
from app.admin import router as admin_router
from config.settings import PORT

Path("data/logs").mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data/logs/app.log", encoding="utf-8"),
    ],
)

app = FastAPI(title="Mentor AN", version="0.2.0", docs_url=None, redoc_url=None)

# Routes first, static mount last
app.include_router(webhook_router)
app.include_router(admin_router)

app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Mentor AN"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
