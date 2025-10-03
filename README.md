# 🌍 Environment Data Platform

<div align="center">
  <img src="https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=white" alt="React">
  <img src="https://img.shields.io/badge/TypeScript-5.9+-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/TailwindCSS-4.1+-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="TailwindCSS">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</div>

<br>

**Environment Data Platform** là một nền tảng giám sát môi trường thời gian thực được xây dựng với React và FastAPI. Ứng dụng cung cấp giao diện đẹp mắt để thu thập, hiển thị và phân tích dữ liệu môi trường từ nhiều nguồn khác nhau.

## ✨ Tính năng chính

- 🌡️ **Dữ liệu môi trường đa dạng**: Theo dõi thời tiết, chất lượng không khí, nước, tiếng ồn, đất, ánh sáng, nhiệt độ và bức xạ
- 🤖 **Phân tích AI tự động**: Tích hợp AI để đánh giá chất lượng môi trường tổng thể
- 🗺️ **Tìm kiếm theo vị trí**: Hỗ trợ tìm kiếm theo tên thành phố, mã quốc gia hoặc tọa độ GPS
- 📊 **Hiển thị dữ liệu thời gian thực**: Giao diện đẹp mắt với skeleton loading và animations
- 🔄 **Tải dữ liệu progressive**: Tải từng loại dữ liệu riêng biệt để tối ưu hiệu suất
- 🌐 **Đa ngôn ngữ**: Hỗ trợ tiếng Anh và tiếng Việt
- 📱 **Responsive Design**: Giao diện thích ứng với mọi kích thước màn hình
- 🎨 **Modern UI/UX**: Glassmorphism design với gradients và backdrop blur

## 🛠️ Công nghệ sử dụng

### Frontend
- **React 19.1+** - Library UI hiện đại
- **TypeScript 5.9+** - Type safety và better DX
- **Vite** - Build tool nhanh chóng
- **TailwindCSS 4.1+** - Utility-first CSS framework
- **Lucide React** - Beautiful icon set
- **ESLint** - Code linting và formatting

### Backend
- **FastAPI 0.104+** - Modern Python web framework
- **Python 3.11+** - Programming language
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **OpenAI** - AI integration cho phân tích môi trường
- **LangChain** - AI workflow management
- **python-dotenv** - Environment variables management

### DevOps & Tools
- **Environment Variables** - Configuration management
- **CORS** - Cross-origin resource sharing
- **HTTP Client** - API communication với httpx

## 🚀 Cài đặt và chạy dự án

### Yêu cầu hệ thống
- **Node.js** 18+ 
- **Python** 3.11+
- **npm** hoặc **yarn**

### 1. Clone repository
```bash
git clone https://github.com/khanhlc04/EnvironmentOpenSource.git
cd EnvironmentOpenSource
```

### 2. Cài đặt Frontend
```bash
cd Frontend
npm install
```

### 3. Cài đặt Backend
```bash
cd ../Backend
python -m venv .venv

# Windows
.venv\\Scripts\\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Cấu hình Environment Variables

#### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

#### Backend (.env)
```env
OPENAI_API_KEY=your_openai_api_key_here
ENVIRONMENT=development
```

### 5. Chạy ứng dụng

#### Chạy Backend
```bash
cd Backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Chạy Frontend
```bash
cd Frontend
npm run dev
```

Ứng dụng sẽ chạy tại:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📋 API Endpoints

### Environment Data
- `GET /api/v1/environment` - Lấy dữ liệu môi trường tổng quan
- `GET /api/v1/environment?include={type}` - Lấy dữ liệu môi trường theo loại
- `GET /api/v1/environment?city={city}&country={country}` - Lấy dữ liệu theo vị trí
- `GET /api/v1/environment?lat={lat}&lon={lon}` - Lấy dữ liệu theo tọa độ

### Supported Data Types
- `weather` - Dữ liệu thời tiết
- `air` - Chất lượng không khí  
- `water` - Chất lượng nước
- `noise` - Mức độ tiếng ồn
- `soil` - Chất lượng đất
- `light` - Mức độ ánh sáng
- `heat` - Chỉ số nhiệt
- `radiation` - Mức bức xạ
- `environmental_quality` - Phân tích AI tổng thể

## 🎨 Giao diện người dùng

### Các thành phần chính
1. **Header**: Logo, title và language selector
2. **Search Section**: Input fields cho location parameters
3. **Data Types Selection**: Grid buttons để chọn loại dữ liệu
4. **Results Display**: Cards hiển thị dữ liệu với loading states
5. **AI Analysis Block**: Phân tích tự động từ AI
6. **Notifications**: Toast messages cho feedback

### Design System
- **Colors**: Blue to purple gradients với glassmorphism effects
- **Typography**: Modern font stack với hierarchy rõ ràng
- **Spacing**: Consistent spacing system với Tailwind
- **Animations**: Smooth transitions và micro-interactions
- **Icons**: Lucide React icon set

## 📁 Cấu trúc dự án

```
EnvironmentOpenSource/
├── Frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── App.tsx          # Main application component
│   │   ├── App.css          # Global styles
│   │   ├── main.tsx         # Application entry point
│   │   └── vite-env.d.ts    # Vite environment types
│   ├── public/              # Static assets
│   ├── package.json         # Frontend dependencies
│   ├── tsconfig.json        # TypeScript configuration
│   ├── vite.config.ts       # Vite build configuration
│   └── .env                 # Frontend environment variables
├── Backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── main.py          # FastAPI application entry
│   │   ├── models/          # Pydantic models
│   │   ├── routes/          # API route handlers
│   │   └── services/        # Business logic services
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Backend environment variables
│   └── README.md            # Backend documentation
└── README.md                # Main project documentation
```

## 🔧 Scripts có sẵn

### Frontend Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run ESLint
npm run preview      # Preview production build
```

### Backend Scripts
```bash
python -m uvicorn app.main:app --reload    # Development server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000    # Production server
```

## 🌟 Tính năng nổi bật

### Progressive Data Loading
- Dữ liệu được tải từng loại một để tối ưu performance
- Skeleton loading states cho better UX
- Error handling và retry mechanisms

### AI-Powered Analysis
- Tự động phân tích chất lượng môi trường
- Đưa ra insights, risks và recommendations
- Hiển thị both formatted data và raw JSON

### Real-time Notifications
- Toast notifications cho user feedback
- Success, error và info states
- Auto-dismiss sau 3 seconds

### API Transparency
- Hiển thị API endpoints được gọi
- Debug information cho developers
- Clear error messages

## 🤝 Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Để contribute:

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

### Development Guidelines
- Tuân thủ TypeScript best practices
- Sử dụng ESLint và Prettier
- Viết tests cho các tính năng mới
- Update documentation khi cần thiết

## 📄 Giấy phép

Dự án này được phân phối dưới giấy phép **MIT License**. Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

```
MIT License

Copyright (c) 2025 Environment Data Platform

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👥 Tác giả

- **khanhlc04** - *Initial work* - [khanhlc04](https://github.com/khanhlc04)

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) - AI analysis capabilities
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - Frontend library
- [TailwindCSS](https://tailwindcss.com/) - CSS framework
- [Lucide](https://lucide.dev/) - Beautiful icons
- [Vite](https://vitejs.dev/) - Build tool

## 📞 Liên hệ

Nếu bạn có câu hỏi hoặc gợi ý, hãy:
- Tạo [Issue](https://github.com/khanhlc04/EnvironmentOpenSource/issues)
- Liên hệ qua email
- Theo dõi project để nhận updates

---

<div align="center">
  <p>⭐ Đừng quên star project nếu thấy hữu ích!</p>
  <p>Made with ❤️ for a better environment</p>
</div>