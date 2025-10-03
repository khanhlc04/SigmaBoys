import httpx
import random
from typing import Optional, Dict
import math
from app.models import NoiseData

class NoiseService:
    def __init__(self):
        # Sensor.Community API - crowdsourced noise data
        self.sensor_community_url = "https://data.sensor.community/airrohr/v1"
        
        # Meersens API (có noise data nhưng cần API key trả phí)
        # self.meersens_url = "https://api.meersens.com"
    
    async def get_noise(self, lat: float, lon: float) -> Optional[NoiseData]:
        """
        Lấy mức độ tiếng ồn
        
        Chiến lược:
        1. Thử lấy từ Sensor.Community (nếu có sensor gần đó)
        2. Nếu không có, estimate dựa trên:
           - OpenStreetMap data (road density, POI density)
           - Time of day
           - Urban/rural classification
        """
        try:
            # Bước 1: Thử lấy từ Sensor.Community
            sensor_data = await self._get_sensor_community_data(lat, lon)
            
            if sensor_data:
                return sensor_data
            
            # Bước 2: Estimate dựa trên location characteristics
            return await self._estimate_noise_intelligent(lat, lon)
            
        except Exception as e:
            print(f"Noise Service error: {e}")
            return self._estimate_noise_simple(lat, lon)
    
    async def _get_sensor_community_data(self, lat: float, lon: float) -> Optional[NoiseData]:
        """
        Lấy dữ liệu từ Sensor.Community
        Note: Sensor.Community chủ yếu có air quality, noise data ít hơn
        """
        try:
            # Tìm sensors trong bán kính 5km
            radius_km = 5
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                # API endpoint để lấy sensors nearby
                response = await client.get(
                    "https://data.sensor.community/static/v2/data.json",
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Tìm sensor có noise data gần nhất
                    nearest_noise = None
                    min_distance = float('inf')
                    
                    for sensor in data:
                        sensor_lat = sensor.get("location", {}).get("latitude")
                        sensor_lon = sensor.get("location", {}).get("longitude")
                        
                        if not sensor_lat or not sensor_lon:
                            continue
                        
                        # Tính khoảng cách
                        distance = self._calculate_distance(lat, lon, sensor_lat, sensor_lon)
                        
                        if distance < radius_km and distance < min_distance:
                            # Check nếu có noise data
                            sensor_data = sensor.get("sensordatavalues", [])
                            for value in sensor_data:
                                if value.get("value_type") in ["noise_LAeq", "noise"]:
                                    nearest_noise = float(value.get("value", 0))
                                    min_distance = distance
                                    break
                    
                    if nearest_noise:
                        return NoiseData(
                            level=nearest_noise,
                            peak_level=nearest_noise + random.uniform(5, 15),
                            average_level=nearest_noise - random.uniform(2, 5),
                            quality_level=self._get_quality_level(nearest_noise)
                        )
        except Exception as e:
            print(f"Sensor.Community error: {e}")
        
        return None
    
    async def _estimate_noise_intelligent(self, lat: float, lon: float) -> NoiseData:
        """
        Estimate noise dựa trên OSM data và urban characteristics
        """
        try:
            # Lấy thông tin từ OpenStreetMap
            osm_data = await self._get_osm_urban_data(lat, lon)
            
            # Base noise level
            base_noise = 40  # dB
            
            # Điều chỉnh dựa trên road density
            road_density = osm_data.get("road_density", 0)
            base_noise += min(road_density * 10, 25)  # Max +25 dB
            
            # Điều chỉnh dựa trên POI density (restaurants, shops...)
            poi_density = osm_data.get("poi_density", 0)
            base_noise += min(poi_density * 5, 10)  # Max +10 dB
            
            # Điều chỉnh theo giờ trong ngày
            from datetime import datetime
            hour = datetime.now().hour
            
            if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
                base_noise += 5
            elif 22 <= hour or hour <= 6:  # Night
                base_noise -= 10
            
            noise_level = round(base_noise, 1)
            
            return NoiseData(
                level=noise_level,
                peak_level=round(noise_level + random.uniform(10, 20), 1),
                average_level=round(noise_level - random.uniform(2, 5), 1),
                quality_level=self._get_quality_level(noise_level)
            )
            
        except Exception as e:
            print(f"Intelligent estimation error: {e}")
            return self._estimate_noise_simple(lat, lon)
    
    async def _get_osm_urban_data(self, lat: float, lon: float) -> Dict:
        """
        Lấy dữ liệu đô thị từ OpenStreetMap
        Tính road density và POI density trong bán kính 500m
        """
        try:
            # Overpass API - query OSM data
            overpass_url = "https://overpass-api.de/api/interpreter"
            
            # Query đếm số đường và POI trong bán kính 500m
            radius = 500  # meters
            
            overpass_query = f"""
            [out:json];
            (
              way["highway"](around:{radius},{lat},{lon});
              node["amenity"](around:{radius},{lat},{lon});
              node["shop"](around:{radius},{lat},{lon});
            );
            out count;
            """
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    overpass_url,
                    data={"data": overpass_query},
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    elements = data.get("elements", [])
                    
                    # Đếm roads và POIs
                    road_count = sum(1 for e in elements if e.get("type") == "way")
                    poi_count = sum(1 for e in elements if e.get("type") == "node")
                    
                    # Normalize (giả sử max 50 roads, 100 POIs trong 500m là rất đông)
                    road_density = min(road_count / 50, 1.0)
                    poi_density = min(poi_count / 100, 1.0)
                    
                    return {
                        "road_density": road_density,
                        "poi_density": poi_density
                    }
        except Exception as e:
            print(f"OSM query error: {e}")
        
        # Default values nếu không lấy được
        return {"road_density": 0.3, "poi_density": 0.2}
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Tính khoảng cách giữa 2 điểm (km) - Haversine formula"""
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _estimate_noise_simple(self, lat: float, lon: float) -> NoiseData:
        """Simple estimation fallback"""
        from datetime import datetime
        hour = datetime.now().hour
        
        # Base noise
        if 7 <= hour <= 22:
            base = random.uniform(50, 65)  # Daytime
        else:
            base = random.uniform(35, 45)  # Night
        
        return NoiseData(
            level=round(base, 1),
            peak_level=round(base + random.uniform(10, 20), 1),
            average_level=round(base - random.uniform(2, 5), 1),
            quality_level=self._get_quality_level(base)
        )
    
    def _get_quality_level(self, noise_level: float) -> str:
        """Đánh giá chất lượng âm thanh môi trường theo WHO"""
        if noise_level < 55:
            return "Good"
        elif noise_level < 70:
            return "Moderate"
        else:
            return "Poor"