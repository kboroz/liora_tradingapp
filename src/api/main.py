from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.api.routers import health, data, market_data, trades, portfolio, predictions

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 API Starting up...")
    yield
    print("🛑 API Shutting down...")

app = FastAPI(
    title="Liora Trading API",
    description="Algorithmic trading backend",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(health.router, tags=["Health"])
app.include_router(data.router, prefix="/api/v1/data", tags=["Data"])
app.include_router(market_data.router, prefix="/api/v1/market", tags=["Market Data"])
app.include_router(trades.router, prefix="/api/v1/trades", tags=["Trades"])
app.include_router(portfolio.router, prefix="/api/v1/portfolio", tags=["Portfolio"])
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["Predictions"])

