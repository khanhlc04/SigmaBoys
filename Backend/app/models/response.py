from pydantic import BaseModel
from typing import Optional, List
from .location import LocationData
from .weather import WeatherData
from .air import AirQualityData
from .water import WaterQualityData
from .noise import NoiseData
from .soil import SoilData
from .light import LightData
from .heat import HeatData
from .radiation import RadiationData
from .environmental_quality import EnvironmentalQuality

class EnvironmentResponse(BaseModel):
    location: LocationData
    time: str
    weather: Optional[WeatherData] = None
    air: Optional[AirQualityData] = None
    water: Optional[WaterQualityData] = None
    noise: Optional[NoiseData] = None
    soil: Optional[SoilData] = None
    light: Optional[LightData] = None
    heat: Optional[HeatData] = None
    radiation: Optional[RadiationData] = None
    environmental_quality: Optional[EnvironmentalQuality] = None
    sources: List[str] = []