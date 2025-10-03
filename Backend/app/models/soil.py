from pydantic import BaseModel, Field
from typing import Optional

class SoilData(BaseModel):
    moisture: Optional[float] = Field(None, description="%")
    temperature: Optional[float] = Field(None, description="°C")
    ph: Optional[float] = None
    conductivity: Optional[float] = Field(None, description="mS/cm")
    quality_level: Optional[str] = None