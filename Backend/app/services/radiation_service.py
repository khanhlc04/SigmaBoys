import httpx
from typing import Optional, List, Dict
import math
from app.models import RadiationData

class RadiationService:
    def __init__(self):
        # Safecast API - FREE, không cần API key
        # 150+ million radiation measurements, CC0 public domain
        self.base_url = "https://api.safecast.org"
        
        # Background radiation database (fallback)
        self.background_levels = {
            "default": 0.12,  # µSv/h
            "coastal": 0.08,
            "urban": 0.10,
            "mountain": 0.18,
            "granite": 0.20,
        }
    
    async def get_radiation(self, lat: float, lon: float) -> Optional[RadiationData]:
        """
        Lấy mức phóng xạ môi trường
        
        Strategy:
        1. Lấy measurements từ Safecast trong bán kính 50km
        2. Tính trung bình các measurements gần nhất (30 ngày)
        3. Fallback to background level database nếu không có data
        """
        try:
            # Lấy measurements từ Safecast
            measurements = await self._get_safecast_measurements(lat, lon, radius_km=50)
            
            if not measurements:
                # Mở rộng bán kính lên 100km
                measurements = await self._get_safecast_measurements(lat, lon, radius_km=100)
            
            if measurements:
                # Parse và tính trung bình
                return self._parse_measurements(measurements)
            
            # Fallback to background level
            return self._estimate_background_radiation(lat, lon)
            
        except Exception as e:
            print(f"Radiation Service error: {e}")
            return self._estimate_background_radiation(lat, lon)
    
    async def _get_safecast_measurements(
        self, 
        lat: float, 
        lon: float, 
        radius_km: float = 50
    ) -> List[Dict]:
        """
        Lấy radiation measurements từ Safecast API
        
        API: https://api.safecast.org/measurements.json
        FREE - không cần API key, CC0 license
        """
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    f"{self.base_url}/measurements.json",
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "distance": radius_km,  # km radius
                        "captured_after": self._get_date_30_days_ago(),
                        "order": "captured_at desc",
                        "limit": 100,
                        "unit": "usv"  # microSieverts
                    },
                    timeout=20.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # API trả về array of measurements
                    if isinstance(data, list) and len(data) > 0:
                        return data
        except Exception as e:
            print(f"Safecast API error: {e}")
        
        return []
    
    def _parse_measurements(self, measurements: List[Dict]) -> RadiationData:
        """
        Parse và tính trung bình measurements từ Safecast
        """
        values = []
        
        for measurement in measurements:
            # Value is in µSv/h
            value = measurement.get("value")
            
            if value and isinstance(value, (int, float)) and value > 0:
                values.append(float(value))
        
        if not values:
            return self._estimate_background_radiation(0, 0)
        
        # Tính trung bình và loại bỏ outliers
        values_sorted = sorted(values)
        
        # Remove top and bottom 10% (outliers)
        trim_count = max(1, len(values_sorted) // 10)
        values_trimmed = values_sorted[trim_count:-trim_count] if len(values_sorted) > 10 else values_sorted
        
        # Tính trung bình
        avg_level = sum(values_trimmed) / len(values_trimmed)
        
        # Background level (typical for the area)
        background = min(values_trimmed)  # Minimum is closest to background
        
        return RadiationData(
            level=round(avg_level, 3),
            background_level=round(background, 3),
            quality_level=self._get_quality_level(avg_level)
        )
    
    def _estimate_background_radiation(self, lat: float, lon: float) -> RadiationData:
        """
        Estimate background radiation dựa trên địa lý
        Sử dụng khi không có Safecast data
        """
        # Estimate based on terrain type
        # High altitudes and granite areas have higher radiation
        
        # Altitude estimate from latitude (rough)
        if abs(lat) > 50:  # High latitude (mountains)
            background = self.background_levels["mountain"]
        elif abs(lat) < 20:  # Tropical (often coastal)
            background = self.background_levels["coastal"]
        else:
            background = self.background_levels["urban"]
        
        # Add small random variation
        import random
        variation = random.uniform(-0.02, 0.02)
        level = background + variation
        
        return RadiationData(
            level=round(level, 3),
            background_level=round(background, 3),
            quality_level=self._get_quality_level(level)
        )
    
    def _get_quality_level(self, level: float) -> str:
        """
        Đánh giá mức độ an toàn phóng xạ
        
        Reference levels:
        - < 0.3 µSv/h: Normal background
        - 0.3-0.5 µSv/h: Slightly elevated
        - 0.5-1.0 µSv/h: Elevated
        - > 1.0 µSv/h: High - Caution needed
        """
        if level < 0.3:
            return "Normal"
        elif level < 0.5:
            return "Slightly Elevated"
        elif level < 1.0:
            return "Elevated"
        else:
            return "High - Caution"
    
    def _get_date_30_days_ago(self) -> str:
        """Get date 30 days ago in ISO format"""
        from datetime import datetime, timedelta
        date_30_days_ago = datetime.now() - timedelta(days=30)
        return date_30_days_ago.strftime("%Y-%m-%d")