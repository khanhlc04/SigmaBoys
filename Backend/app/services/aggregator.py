from typing import Optional, List
from datetime import datetime
from app.models import EnvironmentResponse, LocationData
from app.services.weather_service import WeatherService
from app.services.air_service import AirQualityService
from app.services.water_service import WaterQualityService
from app.services.noise_service import NoiseService
from app.services.soil_service import SoilService
from app.services.light_service import LightService
from app.services.heat_service import HeatService
from app.services.radiation_service import RadiationService
from app.services.geocoding_service import geocoding_service
from app.services.environmental_ai_service import EnvironmentalAIService

class EnvironmentAggregator:
    """Class chính để gom dữ liệu từ tất cả services"""

    def __init__(self):
        self.weather_service = WeatherService()
        self.air_service = AirQualityService()
        self.water_service = WaterQualityService()
        self.noise_service = NoiseService()
        self.soil_service = SoilService()
        self.light_service = LightService()
        self.heat_service = HeatService()
        self.radiation_service = RadiationService()
        
        # AI Service for environmental quality assessment
        try:
            self.ai_service = EnvironmentalAIService()
        except ValueError as e:
            print(f"Warning: AI Service không khởi tạo được: {e}")
            self.ai_service = None
    
    async def get_environment_data(
        self,
        lat: float,
        lon: float,
        city: Optional[str] = None,
        country: Optional[str] = None,
        include: Optional[List[str]] = None
    ) -> EnvironmentResponse:
        """
        Lấy dữ liệu môi trường tổng hợp
        
        Args:
            lat: Vĩ độ
            lon: Kinh độ
            city: Tên thành phố (optional)
            country: Mã quốc gia (optional)
            include: List các loại data cần lấy (optional)
                    VD: ["weather", "air", "water"]
                    Nếu None thì lấy tất cả
        
        Returns:
            EnvironmentResponse với đầy đủ dữ liệu
        """
        sources = []
        
        # Lấy thông tin location từ geocoding nếu city/country không có
        if not city or not country:
            location_info = await geocoding_service.get_location_info(lat, lon)
            city = city or location_info.get('city')
            country = country or location_info.get('country')
        
        location = LocationData(lat=lat, lon=lon, city=city, country=country)
        
        # Weather - Gọi đầu tiên vì các service khác có thể cần data này
        weather_data = None
        if include is None or "weather" in include:
            weather_data = await self.weather_service.get_weather(lat, lon)
            if weather_data:
                sources.append("OpenWeather")
        
        # Air Quality
        air_data = None
        if include is None or "air" in include:
            air_data = await self.air_service.get_air_quality(lat, lon)
            if air_data:
                sources.append("WAQI")
        
        # Water Quality
        water_data = None
        if include is None or "water" in include:
            water_data = await self.water_service.get_water_quality(lat, lon)
            if water_data:
                sources.append("Water Quality Monitoring")
        
        # Noise
        noise_data = None
        if include is None or "noise" in include:
            noise_data = await self.noise_service.get_noise(lat, lon)
            if noise_data:
                sources.append("Noise Monitoring")
        
        # Soil
        soil_data = None
        if include is None or "soil" in include:
            soil_data = await self.soil_service.get_soil(lat, lon)
            if soil_data:
                sources.append("Soil Monitoring")
        
        # Light
        light_data = None
        if include is None or "light" in include:
            light_data = await self.light_service.get_light(lat, lon)
            if light_data:
                sources.append("Solar Calculation")
        
        # Heat (cần weather_data)
        heat_data = None
        if include is None or "heat" in include:
            heat_data = await self.heat_service.get_heat(lat, lon, weather_data)
            if heat_data:
                sources.append("Heat Index Calculation")
        
        # Radiation
        radiation_data = None
        if include is None or "radiation" in include:
            radiation_data = await self.radiation_service.get_radiation(lat, lon)
            if radiation_data:
                sources.append("Radiation Monitoring")
        
        # Tạo response trước
        response = EnvironmentResponse(
            location=location,
            time=datetime.utcnow().isoformat() + "Z",
            weather=weather_data,
            air=air_data,
            water=water_data,
            noise=noise_data,
            soil=soil_data,
            light=light_data,
            heat=heat_data,
            radiation=radiation_data,
            sources=list(set(sources)) 
        )
        
        # AI Analysis for Environmental Quality
        if self.ai_service and (include is None or "environmental_quality" in include):
            try:
                location_dict = {
                    "lat": lat,
                    "lon": lon, 
                    "city": city,
                    "country": country
                }
                
                env_dict = {
                    "weather": weather_data.dict() if weather_data else None,
                    "air": air_data.dict() if air_data else None,
                    "water": water_data.dict() if water_data else None,
                    "noise": noise_data.dict() if noise_data else None,
                    "soil": soil_data.dict() if soil_data else None,
                    "radiation": radiation_data.dict() if radiation_data else None
                }
                
                # Gọi AI để phân tích
                ai_assessment = await self.ai_service.analyze_environment(location_dict, env_dict)
                response.environmental_quality = ai_assessment
                
                sources.append("OpenAI GPT-4")
                
            except Exception as e:
                print(f"AI analysis failed: {e}")
                # Không add AI assessment nếu lỗi
        
        response.sources = list(set(sources))
        return response