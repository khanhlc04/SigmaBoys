import httpx
from typing import Optional
from app.models import WeatherData
from app.core.config import settings

class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def get_weather(self, lat: float, lon: float) -> Optional[WeatherData]:
        """Lấy thông tin thời tiết từ OpenWeather API"""
        if not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.api_key,
                        "units": "metric"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return WeatherData(
                        temperature=data.get("main", {}).get("temp"),
                        feels_like=data.get("main", {}).get("feels_like"),
                        humidity=data.get("main", {}).get("humidity"),
                        pressure=data.get("main", {}).get("pressure"),
                        wind_speed=data.get("wind", {}).get("speed"),
                        wind_direction=data.get("wind", {}).get("deg"),
                        clouds=data.get("clouds", {}).get("all"),
                        visibility=data.get("visibility"),
                        description=data.get("weather", [{}])[0].get("description")
                    )
        except Exception as e:
            print(f"Weather API error: {e}")
        
        return None