from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import time

from config.settings import settings
from src.api.v1 import ai  # Only import AI endpoint for now
from src.api.middleware.rate_limit import RateLimitMiddleware
from src.services.websocket_service import websocket_manager
from src.utils.logger import setup_logging
from src.cache.redis_client import RedisClient

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready Cursor clone with Gemini AI integration",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly for production
)

app.add_middleware(RateLimitMiddleware)

# Include AI router
app.include_router(ai.router, prefix=f"{settings.API_PREFIX}/ai", tags=["ai"])

# Initialize cache client
cache_client = RedisClient()


# WebSocket endpoint
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, user_id: str = "anonymous"):
    await websocket_manager.connect(websocket, session_id, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.handle_message(session_id, user_id, data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(session_id, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(session_id, user_id)


# Health check endpoint
@app.get("/health")
async def health_check():
    cache_health = await cache_client.health_check()

    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": int(time.time()),
        "cache": cache_health,
        "redis_enabled": settings.REDIS_ENABLED
    }


# Cache status endpoint
@app.get("/cache/status")
async def cache_status():
    """Get cache system status"""
    return await cache_client.health_check()


# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Redis enabled: {settings.REDIS_ENABLED}")
    if settings.REDIS_URL:
        logger.info(f"Redis URL configured: {settings.REDIS_URL}")


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=1 if settings.DEBUG else settings.WORKERS,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
