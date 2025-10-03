import httpx
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from app.models import WaterQualityData

class WaterQualityService:
    def __init__(self):
        # Water Quality Portal - FREE, không cần API key
        # Dữ liệu từ USGS, EPA, và 400+ agencies
        self.base_url = "https://www.waterqualitydata.us/data" 
        
    async def get_water_quality(self, lat: float, lon: float) -> Optional[WaterQualityData]:
        """
        Lấy chất lượng nước từ Water Quality Portal
        API: https://www.waterqualitydata.us/webservices_documentation/
        
        Chiến lược:
        1. Tìm monitoring stations trong bán kính 50km
        2. Lấy dữ liệu gần nhất (30 ngày)
        3. Parse và tính trung bình
        """
        try:
            # Bước 1: Tìm stations gần vị trí
            stations = await self._find_nearby_stations(lat, lon, radius_km=50)
            
            if not stations:
                # Fallback: Mở rộng bán kính lên 100km
                stations = await self._find_nearby_stations(lat, lon, radius_km=100)
            
            if not stations:
                # Không có station nào, dùng data giả
                return self._simulate_water_quality(lat, lon)
            
            # Bước 2: Lấy measurements gần nhất từ stations
            measurements = await self._fetch_recent_measurements(stations[:5])  # Top 5 stations
            
            if not measurements:
                return self._simulate_water_quality(lat, lon)
            
            # Bước 3: Parse và aggregate data
            return self._parse_measurements(measurements)
            
        except Exception as e:
            print(f"Water Quality Service error: {e}")
            # Fallback to simulation
            return self._simulate_water_quality(lat, lon)
    
    async def _find_nearby_stations(
        self, 
        lat: float, 
        lon: float, 
        radius_km: float = 50
    ) -> List[Dict]:
        """
        Tìm monitoring stations trong bán kính
        
        API Endpoint: /Station/search
        """
        try:
            # Tính bounding box
            # 1 degree lat ≈ 111km
            # 1 degree lon ≈ 111km * cos(lat)
            import math
            lat_offset = radius_km / 111.0
            lon_offset = radius_km / (111.0 * math.cos(math.radians(lat)))
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/Station/search",
                    params={
                        "bBox": f"{lon-lon_offset},{lat-lat_offset},{lon+lon_offset},{lat+lat_offset}",
                        "siteType": "Stream,Lake,Estuary,Well",  # Loại nguồn nước
                        "mimeType": "json",
                        "sorted": "no"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Trả về list các stations
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and "features" in data:
                        return data["features"]
                    
        except Exception as e:
            print(f"Error finding stations: {e}")
        
        return []
    
    async def _fetch_recent_measurements(self, stations: List[Dict]) -> List[Dict]:
        """
        Lấy measurements từ các stations (30 ngày gần nhất)
        
        API Endpoint: /Result/search
        """
        try:
            # Lấy station IDs
            station_ids = []
            for station in stations:
                if isinstance(station, dict):
                    # Format có thể khác nhau
                    station_id = station.get("MonitoringLocationIdentifier") or \
                                station.get("properties", {}).get("MonitoringLocationIdentifier")
                    if station_id:
                        station_ids.append(station_id)
            
            if not station_ids:
                return []
            
            # Lấy data 30 ngày gần nhất
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/Result/search",
                    params={
                        "siteid": ";".join(station_ids[:5]),  # Giới hạn 5 stations
                        "startDateLo": start_date.strftime("%m-%d-%Y"),
                        "startDateHi": end_date.strftime("%m-%d-%Y"),
                        "characteristicName": "pH;Dissolved oxygen (DO);Turbidity;Specific conductance;Temperature, water",
                        "mimeType": "json",
                        "sorted": "no"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and "results" in data:
                        return data["results"]
                    
        except Exception as e:
            print(f"Error fetching measurements: {e}")
        
        return []
    
    def _parse_measurements(self, measurements: List[Dict]) -> WaterQualityData:
        """
        Parse và tính trung bình các measurements
        """
        # Khởi tạo accumulators
        ph_values = []
        do_values = []  # Dissolved Oxygen
        turbidity_values = []
        conductivity_values = []
        temp_values = []
        
        for measurement in measurements:
            char_name = measurement.get("CharacteristicName", "").lower()
            result_value = measurement.get("ResultMeasureValue")
            
            if not result_value:
                continue
            
            try:
                value = float(result_value)
                
                if "ph" in char_name:
                    ph_values.append(value)
                elif "dissolved oxygen" in char_name or "do" in char_name:
                    do_values.append(value)
                elif "turbidity" in char_name:
                    turbidity_values.append(value)
                elif "conductance" in char_name:
                    conductivity_values.append(value)
                elif "temperature" in char_name:
                    temp_values.append(value)
            except:
                continue
        
        # Tính trung bình
        def avg(values):
            return sum(values) / len(values) if values else None
        
        ph = avg(ph_values)
        do = avg(do_values)
        turbidity = avg(turbidity_values)
        conductivity = avg(conductivity_values)
        temperature = avg(temp_values)
        
        # Đánh giá quality level
        quality_level = self._get_quality_level(ph, do)
        
        return WaterQualityData(
            ph=round(ph, 2) if ph else None,
            dissolved_oxygen=round(do, 2) if do else None,
            turbidity=round(turbidity, 2) if turbidity else None,
            conductivity=round(conductivity, 1) if conductivity else None,
            temperature=round(temperature, 1) if temperature else None,
            quality_level=quality_level
        )
    
    def _get_quality_level(self, ph: Optional[float], do: Optional[float]) -> str:
        """Đánh giá chất lượng nước"""
        if ph is None and do is None:
            return "Unknown"
        
        # pH lý tưởng: 6.5-8.5
        # DO lý tưởng: > 6 mg/L
        ph_ok = ph is None or (6.5 <= ph <= 8.5)
        do_ok = do is None or do >= 6
        
        if ph_ok and do_ok:
            return "Good"
        elif (ph is None or 6.0 <= ph <= 9.0) and (do is None or do >= 4):
            return "Moderate"
        else:
            return "Poor"
    
    def _simulate_water_quality(self, lat: float, lon: float) -> WaterQualityData:
        """Fallback: Dữ liệu giả khi không có API data"""
        import random
        return WaterQualityData(
            ph=round(random.uniform(6.5, 7.8), 2),
            dissolved_oxygen=round(random.uniform(7.0, 9.0), 2),
            turbidity=round(random.uniform(1.0, 5.0), 2),
            conductivity=round(random.uniform(400, 600), 1),
            temperature=round(random.uniform(18, 25), 1),
            quality_level="Simulated"
        )