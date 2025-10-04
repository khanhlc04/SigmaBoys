from fastapi import APIRouter, Query
from typing import Optional
from app.models import EnvironmentResponse
from app.services.aggregator import EnvironmentAggregator
from app.services.geocoding_service import GeocodingService
from app.services.cache_service import cache_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
aggregator = EnvironmentAggregator()
geocoding_service = GeocodingService()

@router.get("/environment", response_model=EnvironmentResponse)
async def get_environment(
    lat: Optional[float] = Query(None, description="Vĩ độ"),
    lon: Optional[float] = Query(None, description="Kinh độ"),
    city: Optional[str] = Query(None, description="Tên thành phố"),
    country: Optional[str] = Query(None, description="Mã quốc gia"),
    include: Optional[str] = Query(
        None,
        description="Các loại dữ liệu cần lấy (phân cách bởi dấu phẩy)"
    )
):
    """
    Lấy dữ liệu môi trường tổng hợp
    
    Có thể sử dụng một trong hai cách:
    1. Với tọa độ: /api/v1/environment?lat=21.0285&lon=105.8542
    2. Với tên thành phố: /api/v1/environment?city=Hanoi&country=Vietnam
    3. Kết hợp: /api/v1/environment?lat=21.0285&lon=105.8542&city=Hanoi
    """
    
    # Xử lý input coordinates
    final_lat = lat
    final_lon = lon
    final_city = city
    final_country = country
    
    # Case 1: Có city nhưng không có coordinates -> Forward geocoding
    if city and (lat is None or lon is None):
        print(f"Forward geocoding for city: {city}")
        final_lat, final_lon = await geocoding_service.get_coordinates_from_city(city, country)
        final_city = city
        final_country = country
    
    # Case 2: Có coordinates nhưng không có city -> Reverse geocoding sẽ được xử lý trong aggregator
    elif lat is not None and lon is not None and not city:
        final_lat = lat
        final_lon = lon
        # city sẽ được lấy từ reverse geocoding trong aggregator
    
    # Case 3: Có cả coordinates và city -> Ưu tiên coordinates
    elif lat is not None and lon is not None and city:
        final_lat = lat
        final_lon = lon
        final_city = city
        final_country = country
    
    # Case 4: Không có gì -> Error
    else:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400, 
            detail="Cần cung cấp ít nhất tọa độ (lat, lon) hoặc tên thành phố (city)"
        )
    
    # Parse include list
    include_list = None
    if include:
        include_list = [item.strip() for item in include.split(",")]
    
    print(f"Final coordinates: ({final_lat}, {final_lon}), city: {final_city}")
    
    # Check cache first - only for queries without include parameter
    if include_list is None:
        logger.info("Checking cache for full environment data")
        cached_data = await cache_service.get_cached_data(
            final_city, final_country, final_lat, final_lon
        )
        if cached_data:
            logger.info("Returning cached data")
            return EnvironmentResponse(**cached_data)
    
    # Get fresh data
    response = await aggregator.get_environment_data(
        final_lat, final_lon, final_city, final_country, include_list
    )
    
    # Save to cache only if no include parameter (full data)
    if include_list is None:
        logger.info("Saving full environment data to cache")
        await cache_service.save_data(
            final_city, final_country, final_lat, final_lon, 
            response.dict()
        )
    
    return response