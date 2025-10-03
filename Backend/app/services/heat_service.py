from typing import Optional
from app.models import HeatData, WeatherData

class HeatService:
    def __init__(self):
        pass
    
    async def get_heat(
        self, 
        lat: float, 
        lon: float, 
        weather_data: Optional[WeatherData]
    ) -> Optional[HeatData]:
        """
        Lấy thông tin nhiệt
        Sử dụng data từ weather service nếu có
        """
        try:
            if not weather_data or weather_data.temperature is None:
                return None
            
            temp = weather_data.temperature
            humidity = weather_data.humidity or 50
            
            # Tính Heat Index (cảm giác nóng)
            heat_index = self._calculate_heat_index(temp, humidity)
            
            # Ước tính nhiệt độ bề mặt (surface temperature)
            # Thường cao hơn không khí 5-15°C vào ban ngày
            surface_temp = self._estimate_surface_temperature(temp, lat, lon)
            
            return HeatData(
                temperature=temp,
                heat_index=heat_index,
                surface_temperature=surface_temp
            )
            
        except Exception as e:
            print(f"Heat Service error: {e}")
            return None
    
    def _calculate_heat_index(self, temp_c: float, humidity: float) -> float:
        """
        Tính Heat Index (Chỉ số nóng ẩm)
        Công thức Steadman's
        """
        # Chỉ tính khi nhiệt độ >= 27°C
        if temp_c < 27:
            return temp_c
        
        # Chuyển sang Fahrenheit để tính
        temp_f = temp_c * 9/5 + 32
        
        # Công thức Heat Index (Rothfusz regression)
        hi = -42.379 + 2.04901523 * temp_f + 10.14333127 * humidity
        hi -= 0.22475541 * temp_f * humidity
        hi -= 0.00683783 * temp_f * temp_f
        hi -= 0.05481717 * humidity * humidity
        hi += 0.00122874 * temp_f * temp_f * humidity
        hi += 0.00085282 * temp_f * humidity * humidity
        hi -= 0.00000199 * temp_f * temp_f * humidity * humidity
        
        # Chuyển về Celsius
        hi_c = (hi - 32) * 5/9
        
        return round(hi_c, 1)
    
    def _estimate_surface_temperature(self, air_temp: float, lat: float, lon: float) -> float:
        """
        Ước tính nhiệt độ bề mặt
        Dựa trên nhiệt độ không khí và thời gian trong ngày
        """
        from datetime import datetime
        
        hour = datetime.now().hour
        
        # Ban ngày (10AM-4PM): bề mặt nóng hơn nhiều
        if 10 <= hour <= 16:
            delta = 8 + (14 - hour) * 0.5  # Cao nhất vào 12-2PM
        # Sáng sớm/chiều tối
        elif 7 <= hour < 10 or 16 < hour <= 19:
            delta = 3
        # Đêm: bề mặt mát hơn không khí
        else:
            delta = -2
        
        surface_temp = air_temp + delta
        return round(surface_temp, 1)
