from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Zundan Studio API",
    description="API for Zundamon video generation",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "zundan-studio-api"}


@app.get("/")
async def root():
    return {"message": "Zundan Studio API", "version": "2.0.0", "docs": "/docs"}


outputs_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outputs"
)
if os.path.exists(outputs_dir):
    app.mount(
        "/outputs", StaticFiles(directory=outputs_dir, html=False), name="outputs"
    )
    logger.info(f"Mounted outputs directory: {outputs_dir}")
else:
    logger.warning(f"Outputs directory not found: {outputs_dir}")

assets_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets"
)
assets_dir = os.path.abspath(assets_dir)

if os.path.exists(assets_dir):
    backgrounds_dir = os.path.join(assets_dir, "backgrounds")
    logger.info(f"Assets directory: {assets_dir}")
    logger.info(f"Backgrounds directory exists: {os.path.exists(backgrounds_dir)}")
    if os.path.exists(backgrounds_dir):
        bg_files = os.listdir(backgrounds_dir)
        logger.info(f"Background files count: {len(bg_files)}")
        if bg_files:
            logger.info(f"Sample background files: {bg_files[:5]}")

    app.mount("/assets", StaticFiles(directory=assets_dir, html=False), name="assets")
    logger.info(f"Mounted assets directory: {assets_dir} at /assets")
else:
    logger.warning(f"Assets directory not found: {assets_dir}")
# Import and include routers
from app.api import videos, scripts, voices, management, websocket

app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(scripts.router, prefix="/api/scripts", tags=["scripts"])
app.include_router(voices.router, prefix="/api/voices", tags=["voices"])
app.include_router(management.router, prefix="/api/management", tags=["management"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
