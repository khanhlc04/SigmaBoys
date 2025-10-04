from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
import uuid

class CachedEnvironmentData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    
    # Cache key fields
    city: Optional[str] = None
    country: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    
    # Data
    data: Dict[str, Any]
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    source: str = "api_call"
    
    class Config:
        populate_by_name = True  # Pydantic v2 syntax