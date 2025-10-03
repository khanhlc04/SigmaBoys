from pydantic import BaseModel, Field
from typing import Optional

class HeatData(BaseModel):
    temperature: Optional[float] = Field(None, description="°C")
    heat_index: Optional[float] = Field(None, description="°C")
    surface_temperature: Optional[float] = Field(None, description="°C")