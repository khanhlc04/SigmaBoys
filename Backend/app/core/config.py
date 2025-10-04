from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Info
    APP_NAME: str = "Environment Data Aggregator"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # ===== API KEYS =====
    # Weather & Soil (same key)
    OPENWEATHER_API_KEY: Optional[str] = None  # Also used for Agromonitoring
    
    # Air Quality
    WAQI_API_KEY: Optional[str] = None
    
    # OpenAI for LangChain
    OPENAI_API_KEY: Optional[str] = None
    
    # ===== FREE APIs (no key needed) =====
    # Water Quality Portal (USGS + EPA) - FREE
    WATER_QUALITY_ENABLED: bool = True
    
    # Noise Monitoring (Sensor.Community + OSM) - FREE
    NOISE_MONITORING_ENABLED: bool = True
    
    # Soil Monitoring (SoilGrids + Agromonitoring) - FREE/Same as OpenWeather
    SOIL_MONITORING_ENABLED: bool = True
    
    # Radiation (Safecast) - FREE
    RADIATION_MONITORING_ENABLED: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # Database
    MONGO_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()