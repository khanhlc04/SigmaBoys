from fastapi import APIRouter
from app.services.cache_service import cache_service
from app.services.database import db_service
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/cache/status")
async def get_cache_status() -> Dict[str, Any]:
    """Get cache system status"""
    return {
        "mongodb_connected": db_service.is_connected(),
        "mongo_url_configured": bool(db_service.client),
        "cache_enabled": db_service.is_connected()
    }

@router.post("/cache/clear-expired")
async def clear_expired_cache() -> Dict[str, Any]:
    """Clear expired cache entries"""
    if not db_service.is_connected():
        return {
            "success": False,
            "message": "MongoDB not connected"
        }
    
    try:
        await cache_service.clear_expired_cache()
        return {
            "success": True,
            "message": "Expired cache entries cleared"
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

@router.get("/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    if not db_service.is_connected():
        return {
            "success": False,
            "message": "MongoDB not connected"
        }
    
    try:
        database = db_service.get_database()
        if database is None:
            return {
                "success": False,
                "message": "Database connection not available"
            }
            
        collection = database[cache_service.COLLECTION_NAME]
        
        total_count = await collection.count_documents({})
        active_count = await collection.count_documents({
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        return {
            "success": True,
            "total_entries": total_count,
            "active_entries": active_count,
            "expired_entries": total_count - active_count
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }