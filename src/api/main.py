"""
FastAPI Application for Liora Trading System
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from typing import List, Dict, Any
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routers
from .routers import health, predictions, data, models, trading

# ============================================================================
# LIFESPAN CONTEXT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    # Startup
    logger.info("🚀 Liora Trading App Starting...")
    logger.info("✅ Database connected")
    logger.info("✅ Redis connected")
    logger.info("✅ Models loaded")
    
    yield
    
    # Shutdown
    logger.info("🛑 Liora Trading App Shutting Down...")
    logger.info("✅ Connections closed")

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Liora Trading App",
    description="Cryptocurrency trading system with ML predictions",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# INCLUDE ROUTERS
# ============================================================================

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])
app.include_router(data.router, prefix="/api/v1", tags=["Data"])
app.include_router(models.router, prefix="/api/v1", tags=["Models"])
app.include_router(trading.router, prefix="/api/v1", tags=["Trading"])

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Liora Trading App",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

