import aiohttp
from typing import Optional, Dict, Any, Tuple
import asyncio

class GeocodingService:
    """Service để geocoding và reverse geocoding"""
    
    def __init__(self):
        self.nominatim_reverse_url = "https://nominatim.openstreetmap.org/reverse"
        self.nominatim_search_url = "https://nominatim.openstreetmap.org/search"
    
    async def get_location_info(self, lat: float, lon: float) -> Dict[str, Any]:
        """Reverse geocoding: Lấy thông tin city/country từ lat/lon"""
        
        try:
            # Sử dụng Nominatim (free)
            async with aiohttp.ClientSession() as session:
                params = {
                    'lat': lat,
                    'lon': lon,
                    'format': 'json',
                    'addressdetails': 1,
                    'accept-language': 'en'
                }
                
                headers = {
                    'User-Agent': 'EnvironmentOpenSource/1.0'
                }
                
                print(f"📡 Calling Nominatim reverse API for ({lat}, {lon})...")
                
                async with session.get(
                    self.nominatim_reverse_url, 
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Geocoding success: {data.get('display_name', 'No display name')}")
                        result = self._parse_nominatim_response(data)
                        print(f"📍 Parsed location: {result}")
                        return result
                    else:
                        return self._get_fallback_location(lat, lon)
                        
        except Exception as e:
            return self._get_fallback_location(lat, lon)
    
    async def get_coordinates_from_city(self, city_name: str, country: Optional[str] = None) -> Tuple[float, float]:
        """Forward geocoding: Convert city name thành lat/lon coordinates"""
        
        try:
            # Tạo query string
            query = city_name
            if country:
                query += f", {country}"
            
            async with aiohttp.ClientSession() as session:
                params = {
                    'q': query,
                    'format': 'json',
                    'addressdetails': 1,
                    'limit': 1,
                    'accept-language': 'en'
                }
                
                headers = {
                    'User-Agent': 'EnvironmentOpenSource/1.0'
                }
                
                print(f"🔍 Searching coordinates for: {query}")
                
                async with session.get(
                    self.nominatim_search_url,
                    params=params, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            result = data[0]
                            lat = float(result['lat'])
                            lon = float(result['lon'])
                            print(f"✅ Found coordinates: {lat}, {lon} for {query}")
                            return lat, lon
                        else:
                            print(f"❌ No results found for {query}")
                            return self._get_fallback_coordinates(city_name)
                    else:
                        print(f"❌ API error: {response.status}")
                        return self._get_fallback_coordinates(city_name)
                        
        except Exception as e:
            print(f"❌ Forward geocoding error: {str(e)}")
            return self._get_fallback_coordinates(city_name)
    
    def _get_fallback_coordinates(self, city_name: str) -> Tuple[float, float]:
        """Fallback coordinates cho một số thành phố nổi tiếng"""
        city_coords = {
            'hanoi': (21.0285, 105.8542),
            'ho chi minh': (10.8231, 106.6297),
            'saigon': (10.8231, 106.6297),
            'da nang': (16.0544, 108.2022),
            'new york': (40.7128, -74.0060),
            'london': (51.5074, -0.1278),
            'paris': (48.8566, 2.3522),
            'tokyo': (35.6762, 139.6503),
            'beijing': (39.9042, 116.4074),
            'shanghai': (31.2304, 121.4737),
            'delhi': (28.6139, 77.2090),
            'mumbai': (19.0760, 72.8777),
            'bangkok': (13.7563, 100.5018),
            'singapore': (1.3521, 103.8198),
            'jakarta': (-6.2088, 106.8456),
            'seoul': (37.5665, 126.9780),
            'sydney': (-33.8688, 151.2093),
            'melbourne': (-37.8136, 144.9631),
        }
        
        city_lower = city_name.lower().strip()
        
        # Tìm exact match
        if city_lower in city_coords:
            return city_coords[city_lower]
        
        # Tìm partial match
        for city, coords in city_coords.items():
            if city_lower in city or city in city_lower:
                return coords
        
        # Default coordinates (Hanoi)
        print(f"⚠️ Using default coordinates for unknown city: {city_name}")
        return (21.0285, 105.8542)
    
    def _parse_nominatim_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse response từ Nominatim"""
        address = data.get('address', {})
        
        # Lấy city (thử nhiều field)
        city = (
            address.get('city') or 
            address.get('town') or 
            address.get('village') or 
            address.get('hamlet') or
            address.get('municipality') or
            'Unknown City'
        )
        
        # Lấy country
        country = address.get('country', 'Unknown Country')
        country_code = address.get('country_code', '').upper()
        
        return {
            'city': city,
            'country': country,
            'country_code': country_code,
            'state': address.get('state'),
            'display_name': data.get('display_name', f"{city}, {country}")
        }
    
    def _get_fallback_location(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fallback khi không lấy được thông tin"""
        # Đoán khu vực dựa trên tọa độ
        if 28.4 <= lat <= 28.8 and 77.0 <= lon <= 77.4:
            return {'city': 'Delhi', 'country': 'India', 'country_code': 'IN'}
        elif 39.7 <= lat <= 40.1 and 116.2 <= lon <= 116.6:
            return {'city': 'Beijing', 'country': 'China', 'country_code': 'CN'}
        elif 64.0 <= lat <= 64.3 and -22.0 <= lon <= -21.5:
            return {'city': 'Reykjavik', 'country': 'Iceland', 'country_code': 'IS'}
        else:
            return {'city': 'Unknown', 'country': 'Unknown', 'country_code': ''}

# Singleton
geocoding_service = GeocodingService()