from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.services.database import db_service
from app.models.cache import CachedEnvironmentData
import logging
import hashlib

logger = logging.getLogger(__name__)

class CacheService:
    COLLECTION_NAME = "environment_data"
    DEFAULT_TTL = 3600  # 1 hour in seconds

    @classmethod
    def _generate_cache_key(cls, city: Optional[str], country: Optional[str], 
                           lat: Optional[float], lon: Optional[float]) -> str:
        """Generate unique cache key from parameters"""
        key_parts = []
        if city:
            key_parts.append(f"city:{city.lower()}")
        if country:
            key_parts.append(f"country:{country.lower()}")
        if lat is not None:
            key_parts.append(f"lat:{lat:.4f}")
        if lon is not None:
            key_parts.append(f"lon:{lon:.4f}")
        
        key_string = "_".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    @classmethod
    async def get_cached_data(cls, city: Optional[str], country: Optional[str],
                             lat: Optional[float], lon: Optional[float]) -> Optional[Dict[str, Any]]:
        """Get cached data if exists and not expired"""
        if not db_service.is_connected():
            logger.debug("MongoDB not connected, cache disabled")
            return None

        try:
            collection = db_service.get_database()[cls.COLLECTION_NAME]
            
            # Find by coordinates or city
            query = {}
            if lat is not None and lon is not None:
                # Match by coordinates with tolerance
                tolerance = 0.01  # ~1km tolerance
                query = {
                    "lat": {"$gte": lat - tolerance, "$lte": lat + tolerance},
                    "lon": {"$gte": lon - tolerance, "$lte": lon + tolerance}
                }
            elif city:
                query = {"city": city.lower()}
                if country:
                    query["country"] = country.lower()
            else:
                return None

            # Add expiration check
            query["expires_at"] = {"$gt": datetime.utcnow()}

            result = await collection.find_one(query, sort=[("created_at", -1)])
            
            if result:
                logger.info(f"Cache hit for query: {query}")
                return result["data"]
            else:
                logger.debug(f"Cache miss for query: {query}")
                return None

        except Exception as e:
            logger.error(f"Error retrieving cached data: {e}")
            return None

    @classmethod
    async def save_data(cls, city: Optional[str], country: Optional[str],
                       lat: Optional[float], lon: Optional[float], 
                       data: Dict[str, Any], ttl_seconds: int = None) -> bool:
        """Save data to cache"""
        if not db_service.is_connected():
            logger.debug("MongoDB not connected, cache disabled")
            return False

        try:
            collection = db_service.get_database()[cls.COLLECTION_NAME]
            
            ttl = ttl_seconds or cls.DEFAULT_TTL
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)

            cache_doc = CachedEnvironmentData(
                city=city.lower() if city else None,
                country=country.lower() if country else None,
                lat=lat,
                lon=lon,
                data=data,
                expires_at=expires_at
            )

            await collection.insert_one(cache_doc.dict(by_alias=True))
            logger.info(f"Cached data for city={city}, lat={lat}, lon={lon}")
            return True

        except Exception as e:
            logger.error(f"Error saving cached data: {e}")
            return False

    @classmethod
    async def clear_expired_cache(cls):
        """Remove expired cache entries"""
        if not db_service.is_connected():
            return

        try:
            collection = db_service.get_database()[cls.COLLECTION_NAME]
            result = await collection.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            logger.info(f"Cleared {result.deleted_count} expired cache entries")
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")

# Global cache instance
cache_service = CacheService()