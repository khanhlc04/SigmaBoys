from pydantic import BaseModel, Field
from typing import Optional

class NoiseData(BaseModel):
    level: Optional[float] = Field(None, description="dB")
    peak_level: Optional[float] = Field(None, description="dB")
    average_level: Optional[float] = Field(None, description="dB")
    quality_level: Optional[str] = None