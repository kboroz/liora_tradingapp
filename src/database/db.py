from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

class DatabaseManager:
    @staticmethod
    async def init():
        async with engine.begin() as conn:
            pass
    
    @staticmethod
    async def close():
        await engine.dispose()
    
    @staticmethod
    def health_check():
        """Placeholder health check - will be async in production"""
        return True
