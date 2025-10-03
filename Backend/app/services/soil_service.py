import httpx
from typing import Optional, Dict
from app.models import SoilData
from app.core.config import settings

class SoilService:
    def __init__(self):
        # Agromonitoring API (same company as OpenWeather)
        self.agro_base_url = "http://api.agromonitoring.com/agro/1.0"
        self.agro_api_key = settings.OPENWEATHER_API_KEY  # Dùng chung với OpenWeather
        
        # SoilGrids API (ISRIC) - FREE, không cần key
        self.soilgrids_url = "https://rest.isric.org/soilgrids/v2.0"
    
    async def get_soil(self, lat: float, lon: float) -> Optional[SoilData]:
        """
        Lấy thông tin đất
        
        Strategy:
        1. Lấy real-time data từ Agromonitoring (moisture + temperature)
        2. Lấy static properties từ SoilGrids (pH + conductivity estimate)
        3. Combine cả 2 sources
        """
        try:
            # Lấy real-time soil data từ Agromonitoring
            agro_data = await self._get_agromonitoring_data(lat, lon)
            
            # Lấy soil properties từ SoilGrids
            soilgrids_data = await self._get_soilgrids_data(lat, lon)
            
            # Combine data
            return self._combine_soil_data(agro_data, soilgrids_data)
            
        except Exception as e:
            print(f"Soil Service error: {e}")
            return self._simulate_soil_data(lat, lon)
    
    async def _get_agromonitoring_data(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Lấy soil moisture và temperature từ Agromonitoring
        
        API: http://api.agromonitoring.com/agro/1.0/soil
        Note: Cần tạo polygon trước, hoặc dùng lat/lon trực tiếp
        """
        if not self.agro_api_key:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Tạo polygon ID tạm (hoặc có thể dùng lat/lon)
                # API này cần polygon ID, nhưng có thể hack bằng cách tạo polygon nhỏ
                
                # Alternative: Dùng endpoint khác cho satellite data
                response = await client.get(
                    f"{self.agro_base_url}/soil",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.agro_api_key
                    },
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse response
                    # t10: Temperature at 10cm depth (Kelvin)
                    # t0: Surface temperature (Kelvin)
                    # moisture: Soil moisture (m3/m3)
                    
                    temp_10cm_k = data.get("t10")
                    moisture = data.get("moisture")
                    
                    if temp_10cm_k and moisture:
                        # Convert Kelvin to Celsius
                        temp_c = temp_10cm_k - 273.15
                        
                        # Convert moisture to percentage
                        moisture_percent = moisture * 100
                        
                        return {
                            "temperature": round(temp_c, 1),
                            "moisture": round(moisture_percent, 1)
                        }
        except Exception as e:
            print(f"Agromonitoring error: {e}")
        
        return None
    
    async def _get_soilgrids_data(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Lấy soil properties từ SoilGrids (pH, organic carbon, etc.)
        
        API: https://rest.isric.org/soilgrids/v2.0/properties/query
        FREE - không cần API key
        """
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    f"{self.soilgrids_url}/properties/query",
                    params={
                        "lon": lon,
                        "lat": lat,
                        "property": ["phh2o", "soc", "clay"],  # pH, organic carbon, clay content
                        "depth": "0-5cm",
                        "value": "mean"
                    },
                    timeout=20.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse properties
                    properties = data.get("properties", {})
                    layers = properties.get("layers", [])
                    
                    ph = None
                    conductivity = None
                    
                    for layer in layers:
                        name = layer.get("name")
                        depths = layer.get("depths", [])
                        
                        if depths and len(depths) > 0:
                            value = depths[0].get("values", {}).get("mean")
                            
                            if name == "phh2o" and value:
                                # pH * 10 (need to divide by 10)
                                ph = value / 10.0
                            
                            elif name == "clay" and value:
                                # Clay content can estimate conductivity
                                # Higher clay = higher conductivity
                                # Clay is in g/kg, convert to rough conductivity estimate
                                conductivity = (value / 100) * 1.5  # Rough estimate
                    
                    if ph or conductivity:
                        return {
                            "ph": round(ph, 2) if ph else None,
                            "conductivity": round(conductivity, 2) if conductivity else None
                        }
        except Exception as e:
            print(f"SoilGrids error: {e}")
        
        return None
    
    def _combine_soil_data(
        self, 
        agro_data: Optional[Dict], 
        soilgrids_data: Optional[Dict]
    ) -> SoilData:
        """
        Combine data từ 2 sources
        """
        # Initialize with defaults
        moisture = None
        temperature = None
        ph = None
        conductivity = None
        
        # From Agromonitoring (real-time)
        if agro_data:
            moisture = agro_data.get("moisture")
            temperature = agro_data.get("temperature")
        
        # From SoilGrids (static)
        if soilgrids_data:
            ph = soilgrids_data.get("ph")
            conductivity = soilgrids_data.get("conductivity")
        
        # If we got at least some data
        if moisture or temperature or ph or conductivity:
            quality_level = self._get_quality_level(ph, moisture)
            
            return SoilData(
                moisture=moisture,
                temperature=temperature,
                ph=ph,
                conductivity=conductivity,
                quality_level=quality_level
            )
        
        # Fallback to simulation
        return self._simulate_soil_data(0, 0)
    
    def _get_quality_level(
        self, 
        ph: Optional[float], 
        moisture: Optional[float]
    ) -> str:
        """Đánh giá chất lượng đất"""
        # pH ideal: 6.0-7.5
        # Moisture ideal: 25-40%
        
        if ph is None and moisture is None:
            return "Unknown"
        
        ph_ok = ph is None or (6.0 <= ph <= 7.5)
        moisture_ok = moisture is None or (25 <= moisture <= 40)
        
        if ph_ok and moisture_ok:
            return "Good"
        elif (ph is None or 5.5 <= ph <= 8.0) and (moisture is None or 15 <= moisture <= 50):
            return "Moderate"
        else:
            return "Poor"
    
    def _simulate_soil_data(self, lat: float, lon: float) -> SoilData:
        """Fallback: simulation"""
        import random
        from datetime import datetime
        
        # Moisture by season
        month = datetime.now().month
        if 5 <= month <= 10:
            moisture = random.uniform(35, 50)
        else:
            moisture = random.uniform(20, 35)
        
        return SoilData(
            moisture=round(moisture, 1),
            temperature=round(20 + random.uniform(-5, 10), 1),
            ph=round(random.uniform(6.0, 7.5), 2),
            conductivity=round(random.uniform(0.5, 1.2), 2),
            quality_level="Simulated"
        )

