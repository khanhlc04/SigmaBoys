from pydantic import BaseModel, Field
from typing import Optional

class WeatherData(BaseModel):
    temperature: Optional[float] = Field(None, description="°C")
    feels_like: Optional[float] = Field(None, description="°C")
    humidity: Optional[float] = Field(None, description="%")
    pressure: Optional[float] = Field(None, description="hPa")
    wind_speed: Optional[float] = Field(None, description="m/s")
    wind_direction: Optional[float] = Field(None, description="degrees")
    clouds: Optional[float] = Field(None, description="%")
    visibility: Optional[float] = Field(None, description="m")
    description: Optional[str] = None
    uv_index: Optional[float] = None