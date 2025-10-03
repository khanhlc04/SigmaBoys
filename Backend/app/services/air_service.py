import httpx
from typing import Optional
from app.models import AirQualityData
from app.core.config import settings

class AirQualityService:
    def __init__(self):
        self.api_key = settings.WAQI_API_KEY
        self.base_url = "https://api.waqi.info"
    
    async def get_air_quality(self, lat: float, lon: float) -> Optional[AirQualityData]:
        """Lấy chất lượng không khí từ WAQI API"""
        if not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/feed/geo:{lat};{lon}/",
                    params={"token": self.api_key},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    iaqi = data.get("iaqi", {})
                    aqi = data.get("aqi")
                    
                    return AirQualityData(
                        aqi=aqi,
                        pm25=iaqi.get("pm25", {}).get("v"),
                        pm10=iaqi.get("pm10", {}).get("v"),
                        o3=iaqi.get("o3", {}).get("v"),
                        no2=iaqi.get("no2", {}).get("v"),
                        so2=iaqi.get("so2", {}).get("v"),
                        co=iaqi.get("co", {}).get("v"),
                        quality_level=self._get_quality_level(aqi)
                    )
        except Exception as e:
            print(f"Air Quality API error: {e}")
        
        return None
    
    def _get_quality_level(self, aqi: Optional[int]) -> Optional[str]:
        """Chuyển AQI thành level đọc được"""
        if aqi is None:
            return None
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"