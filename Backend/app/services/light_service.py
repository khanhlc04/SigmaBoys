import httpx
from typing import Optional
from datetime import datetime, timedelta
import math
from app.models import LightData

class LightService:
    def __init__(self):
        pass
    
    async def get_light(self, lat: float, lon: float) -> Optional[LightData]:
        """
        Lấy thông tin ánh sáng
        Tính toán sunrise/sunset dựa trên tọa độ
        """
        try:
            # Tính sunrise/sunset
            sunrise, sunset = self._calculate_sun_times(lat, lon)
            
            # Tính daylight duration
            daylight_hours = (sunset - sunrise).total_seconds() / 3600
            
            # Ước tính intensity dựa trên thời gian trong ngày
            intensity = self._estimate_light_intensity(sunrise, sunset)
            
            # UV index (có thể lấy từ weather API)
            uv_index = self._estimate_uv_index(lat)
            
            return LightData(
                intensity=intensity,
                uv_index=uv_index,
                sunrise=sunrise.strftime("%H:%M:%S"),
                sunset=sunset.strftime("%H:%M:%S"),
                daylight_duration=round(daylight_hours, 2)
            )
            
        except Exception as e:
            print(f"Light Service error: {e}")
            return None
    
    def _calculate_sun_times(self, lat: float, lon: float) -> tuple:
        """
        Tính sunrise và sunset (thuật toán đơn giản hóa)
        Sử dụng công thức gần đúng
        """
        now = datetime.now()
        
        # Đơn giản hóa: dùng giá trị trung bình cho Việt Nam
        # Thực tế nên dùng thư viện như ephem hoặc astral
        if 8 <= lat <= 23:  # Việt Nam
            sunrise = now.replace(hour=5, minute=45, second=0, microsecond=0)
            sunset = now.replace(hour=18, minute=15, second=0, microsecond=0)
        else:
            # Giá trị mặc định
            sunrise = now.replace(hour=6, minute=0, second=0, microsecond=0)
            sunset = now.replace(hour=18, minute=0, second=0, microsecond=0)
        
        return sunrise, sunset
    
    def _estimate_light_intensity(self, sunrise: datetime, sunset: datetime) -> float:
        """
        Ước tính cường độ ánh sáng (lux)
        Dựa trên thời gian trong ngày
        """
        now = datetime.now()
        
        # Nếu ban đêm: ~1 lux
        if now < sunrise or now > sunset:
            return 1.0
        
        # Ban ngày
        # Noon: ~100,000 lux (trời nắng)
        # Morning/Evening: ~10,000-50,000 lux
        
        # Tính giờ từ sunrise
        hours_since_sunrise = (now - sunrise).total_seconds() / 3600
        total_daylight = (sunset - sunrise).total_seconds() / 3600
        
        # Intensity theo dạng sin (cao nhất vào giữa trưa)
        progress = hours_since_sunrise / total_daylight
        intensity = 100000 * math.sin(progress * math.pi)
        
        return round(max(1000, intensity), 1)
    
    def _estimate_uv_index(self, lat: float) -> float:
        """
        Ước tính UV index
        Càng gần xích đạo UV càng cao
        """
        # Miền nhiệt đới (VN): UV index 6-11
        base_uv = 10 - abs(lat) * 0.2
        
        # Điều chỉnh theo giờ
        now = datetime.now()
        if 10 <= now.hour <= 14:  # UV cao nhất 10AM-2PM
            return round(min(11, base_uv), 1)
        elif 8 <= now.hour <= 16:
            return round(base_uv * 0.7, 1)
        else:
            return 0.0  # Tối không có UV
