import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.webhook import router as webhook_router
from app.admin import router as admin_router
from app.chat import router as chat_router
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

app = FastAPI(title="Mentor AN", version="0.3.0", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

_STATIC = Path(__file__).parent / "static"

# Routes
app.include_router(webhook_router)
app.include_router(admin_router)
app.include_router(chat_router)

# PWA static files
app.mount("/app", StaticFiles(directory=str(_STATIC / "app"), html=True), name="pwa")

# Admin static files
app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Mentor AN", "version": "0.3.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
