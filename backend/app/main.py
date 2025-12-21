from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="Zundan Studio API",
    description="API for Zundamon video generation",
    version="2.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "zundan-studio-api"}


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Zundan Studio API", "version": "2.0.0", "docs": "/docs"}


# Mount static files for outputs
outputs_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outputs"
)
if os.path.exists(outputs_dir):
    app.mount("/outputs", StaticFiles(directory=outputs_dir), name="outputs")

# Import and include routers
from app.api import videos, scripts, voices, management, websocket

app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(scripts.router, prefix="/api/scripts", tags=["scripts"])
app.include_router(voices.router, prefix="/api/voices", tags=["voices"])
app.include_router(management.router, prefix="/api/management", tags=["management"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
