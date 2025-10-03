from pydantic import BaseModel, Field
from typing import Optional

class WaterQualityData(BaseModel):
    ph: Optional[float] = None
    dissolved_oxygen: Optional[float] = Field(None, description="mg/L")
    turbidity: Optional[float] = Field(None, description="NTU")
    conductivity: Optional[float] = Field(None, description="µS/cm")
    temperature: Optional[float] = Field(None, description="°C")
    quality_level: Optional[str] = None