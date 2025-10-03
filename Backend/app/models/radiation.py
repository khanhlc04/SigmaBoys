from pydantic import BaseModel, Field
from typing import Optional

class RadiationData(BaseModel):
    level: Optional[float] = Field(None, description="µSv/h")
    background_level: Optional[float] = Field(None, description="µSv/h")
    quality_level: Optional[str] = None