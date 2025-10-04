from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect_to_mongo(cls):
        """Create database connection"""
        if not settings.MONGO_URL:
            logger.warning("MONGO_URL not configured, MongoDB caching disabled")
            return
            
        try:
            cls.client = AsyncIOMotorClient(settings.MONGO_URL)
            cls.database = cls.client.get_database("environment_cache")
            
            # Test connection
            await cls.client.admin.command('ping')
            logger.info("Connected to MongoDB")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            cls.client = None
            cls.database = None

    @classmethod
    async def close_mongo_connection(cls):
        """Close database connection"""
        if cls.client:
            cls.client.close()
            logger.info("Disconnected from MongoDB")

    @classmethod
    def get_database(cls) -> Optional[AsyncIOMotorDatabase]:
        """Get database instance"""
        return cls.database

    @classmethod
    def is_connected(cls) -> bool:
        """Check if database is connected"""
        return cls.database is not None

# Global database instance
db_service = DatabaseService()