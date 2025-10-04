# 🌍 Environmental Quality API

Một hệ thống API toàn diện để thu thập và phân tích dữ liệu chất lượng môi trường từ nhiều nguồn khác nhau, tích hợp AI để đưa ra đánh giá và khuyến nghị thông minh.

## ✨ Tính năng chính

### 📊 Thu thập dữ liệu đa nguồn
- **Chất lượng không khí**: PM2.5, PM10, AQI, NO2, SO2, CO, O3 từ WAQI
- **Thời tiết**: Nhiệt độ, độ ẩm, UV index từ OpenWeather
- **Chất lượng nước**: pH, oxy hòa tan, độ đục
- **Mức độ tiếng ồn**: Đo lường theo decibel (dB)
- **Chất lượng đất**: pH, độ ẩm, chất dinh dưỡng
- **Bức xạ**: Mức độ bức xạ môi trường

### 🤖 Phân tích AI thông minh
- **Tích hợp OpenAI GPT-4**: Phân tích và đưa ra đánh giá chuyên sâu
- **LangChain**: Framework AI để xử lý dữ liệu phức tạp
- **Đánh giá rủi ro sức khỏe**: Từ thấp đến nghiêm trọng
- **Khuyến nghị cá nhân hóa**: Dựa trên dữ liệu thực tế

### 🗺️ Geocoding thông minh
- **Forward Geocoding**: Chuyển tên thành phố → tọa độ
- **Reverse Geocoding**: Chuyển tọa độ → thông tin địa danh
- **Hỗ trợ đa ngôn ngữ**: Tên thành phố bằng nhiều ngôn ngữ

## 🚀 Cài đặt

### Yêu cầu hệ thống
- Python 3.11+
- MongoDB (Optional - for caching)
- OpenAI API Key
- Kết nối Internet

### 1. Clone repository
```bash
git clone <repository-url>
cd EnvironmentOpenSource
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu hình environment variables
Tạo file `.env` trong thư mục gốc:

```env
# OpenAI API Key (bắt buộc)
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# OpenAI API Key
OPENAI_API_KEY=your-openai-key-here

# Air Quality API
WAQI_API_KEY=your-waqi-token-here

# Weather API (OpenWeather)
OPENWEATHER_API_KEY=your-openweather-key-here

# MongoDB (Optional - for caching)
MONGO_URL=mongodb://localhost:27017
```

### 4. (Optional) Cài đặt MongoDB cho cache
```bash
# Ubuntu/Debian
sudo apt install mongodb

# macOS với Homebrew
brew install mongodb/brew/mongodb-community

# Hoặc sử dụng MongoDB Atlas (cloud)
# Điền MONGO_URL với connection string từ Atlas
```

### 5. Test MongoDB connection (nếu sử dụng cache)
```bash
python test_mongodb.py
```

### 6. Chạy server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ chạy tại: `http://localhost:8000`

## 📖 Sử dụng API

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Endpoint chính

#### 🌍 Lấy dữ liệu môi trường
```http
GET /api/v1/environment
```

**Tham số:**
- `lat` (float, optional): Vĩ độ
- `lon` (float, optional): Kinh độ  
- `city` (string, optional): Tên thành phố
- `country` (string, optional): Tên quốc gia
- `include` (array, optional): Danh sách services cần lấy

#### 💾 Cache Management
```http
GET /api/v1/cache/status      # Kiểm tra trạng thái cache
GET /api/v1/cache/stats       # Thống kê cache
POST /api/v1/cache/clear-expired  # Xóa cache hết hạn
```

**Lưu ý về Cache:**
- Cache chỉ áp dụng cho queries **không có** parameter `include`
- Cache tự động expires sau 1 giờ
- Cải thiện performance đáng kể cho các query thường xuyên

### Ví dụ sử dụng

#### 1. Theo tọa độ địa lý
```bash
curl "http://localhost:8000/api/v1/environment?lat=21.0285&lon=105.8542"
```

#### 2. Theo tên thành phố
```bash
curl "http://localhost:8000/api/v1/environment?city=Hanoi&country=Vietnam"
```

#### 3. Chỉ lấy dữ liệu cụ thể
```bash
curl "http://localhost:8000/api/v1/environment?lat=21.0285&lon=105.8542&include=air&include=weather"
```

### Response mẫu
```json
{
  "location": {
    "lat": 21.0285,
    "lon": 105.8542,
    "city": "Hanoi",
    "country": "Vietnam"
  },
  "time": "2025-10-04T10:30:00Z",
  "weather": {
    "temperature": 28.5,
    "humidity": 75,
    "description": "Partly cloudy",
    "uvi": 6.2
  },
  "air": {
    "aqi": 95,
    "pm25": 35.2,
    "pm10": 45.8,
    "quality_level": "moderate"
  },
  "environmental_quality": {
    "overall_rating": "moderate",
    "score": 72.5,
    "health_risk": "moderate",
    "summary": "Chất lượng không khí ở mức trung bình, cần chú ý với người nhạy cảm",
    "recommendations": [
      "Hạn chế hoạt động ngoài trời vào giờ cao điểm",
      "Sử dụng khẩu trang khi ra đường",
      "Tăng cường thông gió trong nhà"
    ],
    "concerns": [
      "Mức PM2.5 gần ngưỡng WHO",
      "Độ ẩm cao có thể làm tăng cảm giác bức bí"
    ],
    "ai_reasoning": "Dựa trên dữ liệu AQI 95 và PM2.5 35.2μg/m³, chất lượng không khí đang ở mức trung bình..."
  },
  "sources": [
    "OpenWeather",
    "WAQI",
    "OpenAI GPT-4"
  ]
}
```

## 🏗️ Kiến trúc hệ thống

```
app/
├── api/v1/               # API endpoints
│   └── environment.py    # Main environment endpoint
├── core/                 # Core configuration
│   └── config.py        # Settings & environment variables
├── models/              # Data models
│   ├── air.py          # Air quality models
│   ├── weather.py      # Weather models
│   ├── environmental_quality.py  # AI assessment models
│   └── response.py     # Response schemas
├── services/           # Business logic
│   ├── aggregator.py   # Main data aggregation
│   ├── air_service.py  # Air quality service
│   ├── weather_service.py      # Weather service
│   ├── geocoding_service.py    # Location services
│   ├── environmental_ai_service.py  # AI analysis
│   └── ...             # Other environmental services
└── main.py            # FastAPI application
```

## 🔧 Cấu hình nâng cao

### Environment Variables
```env
# Core API Keys
OPENAI_API_KEY=sk-proj-...        # OpenAI cho AI analysis
WAQI_API_KEY=token...             # World Air Quality Index
OPENWEATHER_API_KEY=key...        # OpenWeather cho thời tiết

# Optional configurations
AI_MODEL=gpt-4o-mini              # AI model (default: gpt-4o-mini)
AI_TEMPERATURE=0.1                # AI creativity (0-1)
GEOCODING_TIMEOUT=10              # Geocoding timeout (seconds)
```

### Tuỳ chỉnh AI Analysis
```python
# app/services/environmental_ai_service.py
self.llm = ChatOpenAI(
    model='gpt-4o-mini',     # Có thể đổi thành gpt-4, gpt-3.5-turbo
    temperature=0.1,         # Điều chỉnh độ sáng tạo
    api_key=openai_key
)
```

## 🧪 Testing

### Test cơ bản
```bash
# Test server health
curl http://localhost:8000/

# Test với tọa độ Delhi (thành phố ô nhiễm)
curl "http://localhost:8000/api/v1/environment?lat=28.6139&lon=77.2090"

# Test với tọa độ Iceland (môi trường sạch)
curl "http://localhost:8000/api/v1/environment?lat=64.1466&lon=-21.9426"
```

### Test AI Analysis
```bash
# Test với thành phố ô nhiễm nặng
curl "http://localhost:8000/api/v1/environment?city=Beijing&country=China"

# Test với thành phố môi trường tốt
curl "http://localhost:8000/api/v1/environment?city=Zurich&country=Switzerland"
```

## 📊 Nguồn dữ liệu

| Service | Nguồn | Dữ liệu |
|---------|-------|---------|
| **Air Quality** | WAQI.info | PM2.5, PM10, AQI, NO2, SO2, CO, O3 |
| **Weather** | OpenWeather | Nhiệt độ, độ ẩm, UV index, thời tiết |
| **Geocoding** | Nominatim | Reverse/Forward geocoding miễn phí |
| **AI Analysis** | OpenAI GPT-4 | Phân tích chuyên sâu, khuyến nghị |
| **Water Quality** | Simulated | pH, oxy hòa tan (dữ liệu mô phỏng) |
| **Noise/Soil** | Simulated | Mức tiếng ồn, chất lượng đất |

## 🛠️ Công nghệ & Giấy phép

### Core Technologies

#### **FastAPI** 🚀
- **Phiên bản**: 0.104.1+
- **Giấy phép**: MIT License
- **Mô tả**: Modern, fast web framework cho Python APIs
- **Website**: https://fastapi.tiangolo.com/
- **Lý do chọn**: High performance, auto documentation, async support

#### **Python** 🐍
- **Phiên bản**: 3.11+
- **Giấy phép**: PSF License (Python Software Foundation)
- **Mô tả**: Programming language chính của dự án
- **Website**: https://python.org/

#### **Pydantic** ✅
- **Phiên bản**: 2.0+
- **Giấy phép**: MIT License
- **Mô tả**: Data validation và serialization
- **Website**: https://docs.pydantic.dev/

### AI & Machine Learning Stack

#### **LangChain** 🔗
- **Phiên bản**: 0.3.27+
- **Giấy phép**: MIT License
- **Mô tả**: Framework để xây dựng applications với LLMs
- **Website**: https://langchain.com/
- **Components sử dụng**:
  - `langchain-openai`: OpenAI integration
  - `langchain-core`: Core functionality
  - `langchain-community`: Community extensions

### External APIs

#### **WAQI (World Air Quality Index)** 🌬️
- **Giấy phép**: Free tier với attribution required
- **Website**: https://waqi.info/
- **API Docs**: https://aqicn.org/api/
- **Rate Limits**: 1000 requests/day (free tier)
- **Data License**: Creative Commons Attribution
- **Attribution Required**: "Air quality data from World Air Quality Index project"
- **Terms**: https://aqicn.org/api/tos/

#### **OpenWeather** ☀️
- **Giấy phép**: Freemium (Free tier: 1000 calls/day)
- **Website**: https://openweathermap.org/
- **API Docs**: https://openweathermap.org/api
- **Data License**: ODbL (Open Database License)
- **Commercial Use**: Allowed với proper subscription
- **Rate Limits**: 60 calls/minute (free tier)
- **Terms**: https://openweathermap.org/terms

#### **Nominatim (OpenStreetMap)** 🗺️
- **Giấy phép**: Open Database License (ODbL)
- **Website**: https://nominatim.org/
- **Data Source**: OpenStreetMap
- **Usage Policy**: https://operations.osmfoundation.org/policies/nominatim/
- **Rate Limits**: 1 request/second
- **Attribution Required**: "© OpenStreetMap contributors"
- **Commercial Use**: Allowed với attribution

### Python Dependencies

#### **Core Web Stack**
```python
fastapi>=0.104.1         # MIT License - Web framework
uvicorn>=0.24.0          # BSD License - ASGI server
pydantic>=2.0            # MIT License - Data validation
starlette>=0.27.0        # BSD License - Web components
```

#### **HTTP & Async**
```python
aiohttp>=3.9.0           # Apache 2.0 - Async HTTP client
httpx>=0.25.0            # BSD License - HTTP client
requests>=2.31.0         # Apache 2.0 - HTTP library
asyncio                  # PSF License - Built-in async
```

#### **AI & ML Libraries**
```python
langchain>=0.3.27        # MIT License - LLM framework
langchain-openai>=0.3.33 # MIT License - OpenAI integration
langchain-core>=0.3.72   # MIT License - Core components
langchain-community>=0.3.29 # MIT License - Community tools
openai>=1.108.1          # Apache 2.0 - OpenAI client
```

#### **Data Processing**
```python
python-dotenv>=1.0.0     # BSD License - Environment variables
python-multipart>=0.0.6  # Apache 2.0 - File uploads
```

#### **Development Tools**
```python
pytest>=7.4.0           # MIT License - Testing framework
black>=23.0.0            # MIT License - Code formatter
flake8>=6.0.0            # MIT License - Linting
mypy>=1.6.0              # MIT License - Type checking
```

### Deployment & Infrastructure

#### **Docker** 🐳
- **Giấy phép**: Apache 2.0 License
- **Website**: https://docker.com/
- **Base Image**: `python:3.11-slim` (Debian-based)

#### **Cloud Platforms** ☁️
- **Heroku**: Commercial platform (Free tier discontinued)
- **Railway**: Freemium ($5/month for hobby projects)
- **DigitalOcean**: Commercial ($4-6/month for basic droplets)
- **AWS/GCP/Azure**: Commercial (Pay-as-you-go)

## 📋 License Compliance

### ✅ Open Source Components
Tất cả dependencies chính sử dụng permissive licenses (MIT, BSD, Apache 2.0) - cho phép:
- ✅ Commercial use
- ✅ Modification  
- ✅ Distribution
- ✅ Private use

### ⚠️ Commercial Components

#### OpenAI API
- **Cost**: ~$0.15 per 1M tokens (GPT-4o-mini)
- **Terms**: Must comply với OpenAI Terms of Service
- **Usage Limits**: Subject to OpenAI's rate limits
- **Content Policy**: Must follow OpenAI's usage policies

#### External APIs Rate Limits
- **WAQI**: 1000 requests/day (free)
- **OpenWeather**: 1000 requests/day (free)  
- **Nominatim**: 1 request/second

### 📝 Required Attributions

```text
Dự án này sử dụng:
- Air quality data from World Air Quality Index project (WAQI)
- Weather data from OpenWeather (© OpenWeather Ltd)
- Map data from OpenStreetMap (© OpenStreetMap contributors)
- AI analysis powered by OpenAI GPT-4
```

### 🔒 Data Privacy Compliance

#### GDPR Compliance
- ✅ Không lưu trữ personal data
- ✅ Không track users
- ✅ Location data chỉ dùng cho API calls
- ✅ Transparent về data usage

#### User Data Handling
- **Location coordinates**: Chỉ dùng để query APIs, không lưu trữ
- **API responses**: Không cache user-specific data
- **Logs**: Chỉ lưu system logs, không có personal info

### 💰 Cost Estimation (Monthly)

#### Development/Testing
```
OpenAI API: $5-10/month (1M tokens)
WAQI Free Tier: $0
OpenWeather Free: $0
Hosting (Railway): $5/month
Total: ~$10-15/month
```

#### Production (1K users/day)
```
OpenAI API: $50-100/month
WAQI Pro: $20/month
OpenWeather Pro: $40/month  
Hosting (DO Droplet): $20/month
Total: ~$130-180/month
```

## 🚨 Xử lý lỗi

### Lỗi thường gặp

#### 1. API Key không hợp lệ
```json
{
  "environmental_quality": {
    "overall_rating": "moderate",
    "ai_reasoning": "Service error: Incorrect API key provided"
  }
}
```
**Giải pháp**: Kiểm tra `.env` file và đảm bảo OPENAI_API_KEY đúng

#### 2. Không tìm thấy tọa độ
```json
{
  "detail": "Không thể tìm thấy tọa độ cho thành phố: InvalidCity"
}
```
**Giải pháp**: Kiểm tra tên thành phố và quốc gia

#### 3. Rate limit exceeded
```json
{
  "detail": "Rate limit exceeded for API service"
}
```
**Giải pháp**: Đợi ít phút hoặc nâng cấp API plan

## 🔒 Bảo mật

- **API Keys**: Lưu trong `.env`, không commit vào git
- **Rate Limiting**: Tích hợp sẵn cho các external APIs
- **Input Validation**: Validate tất cả parameters đầu vào
- **Error Handling**: Không expose sensitive information

## 🚀 Deployment

### Docker (khuyến nghị)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deploy
```bash
# Heroku
git push heroku main

# Railway
railway up

# DigitalOcean App Platform
doctl apps create --spec .do/app.yaml
```

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

## 📋 TODO

- [ ] **Caching**: Redis cache cho dữ liệu môi trường
- [ ] **Database**: PostgreSQL để lưu historical data
- [ ] **Real-time**: WebSocket cho live updates
- [ ] **Mobile API**: Tối ưu cho mobile apps
- [ ] **Dashboard**: Web dashboard để visualize data
- [ ] **Alerts**: Email/SMS alerts cho pollution levels
- [ ] **ML Models**: Custom ML models cho prediction

## 📄 License

MIT License - xem file `LICENSE` để biết chi tiết.

## 👥 Team

- **Developer**: SigmaBoys
- **AI Integration**: Powered by OpenAI GPT-4
- **Data Sources**: WAQI, OpenWeather, và nhiều nguồn khác

**🌱 Made with ❤️ for a cleaner planet** 🌍