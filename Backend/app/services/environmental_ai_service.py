import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import SecretStr
from app.core.config import settings
from app.models.environmental_quality import EnvironmentalQuality

# Load environment variables
load_dotenv()

class EnvironmentalAIService:
    """Service sử dụng OpenAI thông qua LangChain để phân tích chất lượng môi trường"""
    
    def __init__(self):
        # Load .env file
        load_dotenv()
        
        # Lấy OpenAI key từ environment
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("Cần OPENAI_API_KEY trong environment variables (.env file)")
        
        print(f"✓ OpenAI key loaded: {openai_key[:10]}...{openai_key[-4:]}")
        
        # Tạo ChatOpenAI instance
        self.llm = ChatOpenAI(
            model='gpt-4o-mini',
            temperature=0,
            api_key=SecretStr(openai_key)
        )
        print("✓ ChatOpenAI initialized successfully")
    
    async def analyze_environment(self, location_data: Dict[str, Any], env_data: Dict[str, Any]) -> EnvironmentalQuality:
        """
        Phân tích chất lượng môi trường bằng AI
        """
        
        try:
            print(f"🔍 Input data - Location: {location_data}")
            print(f"🔍 Input data - Environment keys: {list(env_data.keys()) if env_data else 'None'}")
            
            # Validate input data
            if not location_data:
                location_data = {"city": "Unknown", "country": "Unknown", "lat": 0, "lon": 0}
            if not env_data:
                env_data = {}
            
            # Tạo prompt để AI phân tích
            prompt = self._create_analysis_prompt(location_data, env_data)
            
            # Validate prompt
            if not prompt or prompt.strip() == "":
                raise ValueError("Generated prompt is empty")
            
            print("Sending request to OpenAI...")
            print(f"Prompt length: {len(prompt)} characters")
            print(f"Prompt preview: {prompt[:200]}...")
            
            # Gọi OpenAI với validation
            message = HumanMessage(content=prompt)
            response = await self.llm.ainvoke([message])
            
            print("✓ Response received from OpenAI")
            
            # Parse kết quả
            content = str(response.content) if hasattr(response, 'content') else str(response)
            result = self._parse_ai_response(content)
            
            return EnvironmentalQuality(**result)
            
        except Exception as e:
            print(f"AI Analysis Error: {str(e)}")
            print(f"Error type: {type(e)}")
            # Fallback nếu AI lỗi
            return self._create_fallback_assessment(str(e))
    
    def _create_analysis_prompt(self, location_data: Dict[str, Any], env_data: Dict[str, Any]) -> str:
        """Tạo prompt chi tiết cho AI"""
        
        try:
            # Format location info
            city = location_data.get('city', 'Unknown') if location_data else 'Unknown'
            country = location_data.get('country', 'Unknown') if location_data else 'Unknown'
            lat = location_data.get('lat', 0) if location_data else 0
            lon = location_data.get('lon', 0) if location_data else 0
            
            location_str = f"Vị trí: {city}, {country} ({lat}, {lon})"
            
            # Format environmental data
            data_summary = []
            
            # Weather data
            if env_data and 'weather' in env_data and env_data['weather']:
                weather = env_data['weather']
                data_summary.append(f"Thời tiết: {weather.get('temperature', 'N/A')}°C, độ ẩm {weather.get('humidity', 'N/A')}%, {weather.get('description', 'N/A')}")
            
            # Air quality data
            if env_data and 'air' in env_data and env_data['air']:
                air = env_data['air']
                data_summary.append(f"Chất lượng không khí: AQI {air.get('aqi', 'N/A')}, PM2.5: {air.get('pm25', 'N/A')} μg/m³, Mức độ: {air.get('quality_level', 'N/A')}")
            
            # Water quality data
            if env_data and 'water' in env_data and env_data['water']:
                water = env_data['water']
                data_summary.append(f"Chất lượng nước: pH {water.get('ph', 'N/A')}, DO {water.get('dissolved_oxygen', 'N/A')} mg/L, Mức độ: {water.get('quality_level', 'N/A')}")
            
            # Noise data
            if env_data and 'noise' in env_data and env_data['noise']:
                noise = env_data['noise']
                noise_level = noise.get('level', noise.get('level_db', 'N/A'))
                data_summary.append(f"Tiếng ồn: {noise_level} dB, Mức độ: {noise.get('quality_level', 'N/A')}")
            
            # Soil data
            if env_data and 'soil' in env_data and env_data['soil']:
                soil = env_data['soil']
                data_summary.append(f"Đất: pH {soil.get('ph', 'N/A')}, độ ẩm {soil.get('moisture', 'N/A')}%")
            
            # Radiation data
            if env_data and 'radiation' in env_data and env_data['radiation']:
                radiation = env_data['radiation']
                data_summary.append(f"Bức xạ: {radiation.get('level', 'N/A')} μSv/h, Mức độ: {radiation.get('quality_level', 'N/A')}")
            
            data_text = "\n".join(data_summary) if data_summary else "Không có dữ liệu môi trường chi tiết"
            
            # Tạo prompt hoàn chỉnh
            prompt = f"""
Bạn là chuyên gia môi trường. Hãy phân tích dữ liệu môi trường sau và đưa ra đánh giá chất lượng môi trường:

{location_str}

DỮ LIỆU MÔI TRƯỜNG:
{data_text}

Hãy phân tích và trả về kết quả dưới dạng JSON với format sau:
{{
    "overall_rating": "excellent|good|moderate|poor|hazardous",
    "score": [số từ 0-100],
    "health_risk": "low|moderate|high|severe",
    "summary": "Tóm tắt ngắn gọn về chất lượng môi trường",
    "recommendations": ["danh sách khuyến nghị"],
    "concerns": ["danh sách những lo ngại"],
    "ai_reasoning": "Giải thích chi tiết về cách đánh giá"
}}

Lưu ý:
- Dựa trên WHO và EPA standards
- AQI >100 là không tốt, >200 là nguy hiểm
- PM2.5 >35 μg/m³ là vượt chuẩn WHO
- pH nước nên trong khoảng 6.5-8.5
- Tiếng ồn >55dB ngày, >40dB đêm là có hại
- Đưa ra khuyến nghị thực tế và hữu ích
"""
            
            result = prompt.strip()
            print(f"✓ Prompt created successfully, length: {len(result)}")
            return result
            
        except Exception as e:
            print(f"Error creating prompt: {str(e)}")
            # Trả về prompt fallback
            return f"""
Phân tích chất lượng môi trường cho vị trí {location_data.get('city', 'Unknown') if location_data else 'Unknown'}.

Hãy trả về JSON format:
{{
    "overall_rating": "moderate",
    "score": 50,
    "health_risk": "moderate",
    "summary": "Không có đủ dữ liệu để phân tích chi tiết",
    "recommendations": ["Cần thu thập thêm dữ liệu môi trường"],
    "concerns": ["Thiếu thông tin môi trường"],
    "ai_reasoning": "Dữ liệu đầu vào không đầy đủ"
}}
"""
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse response từ AI thành dict"""
        try:
            # Loại bỏ markdown nếu có
            clean_response = ai_response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            
            # Parse JSON
            result = json.loads(clean_response.strip())
            
            # Validate và set default values
            result.setdefault("overall_rating", "moderate")
            result.setdefault("score", 50.0)
            result.setdefault("health_risk", "moderate")
            result.setdefault("summary", "Đánh giá môi trường bằng AI")
            result.setdefault("recommendations", [])
            result.setdefault("concerns", [])
            result.setdefault("ai_reasoning", "Phân tích dựa trên dữ liệu môi trường")
            
            return result
            
        except Exception as e:
            print(f"Parse error: {str(e)}")
            print(f"AI Response: {ai_response[:500]}...")
            # Nếu parse lỗi, trả về default
            return {
                "overall_rating": "moderate",
                "score": 50.0,
                "health_risk": "moderate", 
                "summary": f"Lỗi parse AI response: {str(e)}",
                "recommendations": ["Kiểm tra lại dữ liệu môi trường"],
                "concerns": ["Không thể phân tích chính xác"],
                "ai_reasoning": f"AI response parsing error: {ai_response[:200]}..."
            }
    
    def _create_fallback_assessment(self, error: str) -> EnvironmentalQuality:
        """Tạo đánh giá dự phòng khi AI lỗi"""
        return EnvironmentalQuality(
            overall_rating="moderate",
            score=50.0,
            health_risk="moderate",
            summary="Không thể kết nối AI để phân tích",
            recommendations=["Thử lại sau", "Kiểm tra kết nối internet"],
            concerns=["Lỗi hệ thống AI"],
            ai_reasoning=f"Service error: {error}"
        )

# Singleton instance
environmental_ai_service = EnvironmentalAIService()