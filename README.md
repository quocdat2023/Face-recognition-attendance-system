# 👤 Face Recognition System

Hệ thống nhận diện khuôn mặt và điểm danh tự động sử dụng Python, MongoDB, FastAPI, Flask và face-api.js.

## ✨ Tính năng

- 📝 **Đăng ký người dùng**: Chụp ảnh khuôn mặt và lưu thông tin
- 🎯 **Nhận diện real-time**: Nhận diện khuôn mặt từ camera trực tiếp
- ✅ **Điểm danh tự động**: Tự động ghi nhận khi phát hiện khuôn mặt
- 📊 **Thống kê**: Xem lịch sử điểm danh và thống kê
- 🎨 **Giao diện đẹp**: Dark mode với hiệu ứng glassmorphism

## 🏗️ Kiến trúc

- **Backend**: Python với Flask (frontend) + FastAPI (API)
- **Face Recognition**: Thư viện `face_recognition` (dlib) cho mã hóa khuôn mặt
- **Visualization**: face-api.js để vẽ khung và nhãn trên video
- **Database**: MongoDB để lưu trữ dữ liệu người dùng và face encodings
- **Frontend**: HTML/CSS với JavaScript (embedded)

### Luồng hoạt động

**Đăng ký:**
1. Client chụp ảnh từ camera
2. Gửi ảnh lên backend
3. Backend trích xuất face encoding (128-D vector)
4. Lưu vào MongoDB

**Nhận diện:**
1. Client gửi frame video lên backend mỗi giây
2. Backend phát hiện khuôn mặt và so khớp với database
3. Trả về vị trí khuôn mặt + tên người
4. Frontend dùng face-api.js vẽ khung và label
5. Tự động ghi điểm danh

## 📋 Yêu cầu

- Python 3.8+
- MongoDB (local hoặc Atlas)
- Webcam
- CMake (để cài đặt dlib)
- Visual Studio Build Tools (Windows)

## 🚀 Cài đặt

### 1. Clone hoặc tải project

```bash
cd c:\Users\quocd\Videos\face
```

### 2. Cài đặt MongoDB

**Option A: MongoDB Local**
- Tải và cài đặt MongoDB Community Server từ https://www.mongodb.com/try/download/community
- Chạy MongoDB service

**Option B: MongoDB Atlas (Cloud)**
- Đăng ký tài khoản miễn phí tại https://www.mongodb.com/cloud/atlas
- Tạo cluster và lấy connection string
- Cập nhật `MONGODB_URI` trong `app.py`

### 3. Cài đặt Python dependencies

```bash
# Cài đặt CMake (cần cho dlib)
pip install cmake

# Cài đặt các thư viện
pip install -r requirements.txt
```

**Lưu ý cho Windows:**
- Nếu gặp lỗi khi cài `dlib`, cần cài Visual Studio Build Tools
- Tải từ: https://visualstudio.microsoft.com/downloads/
- Chọn "Desktop development with C++"

**Nếu gặp lỗi với face_recognition:**
```bash
# Cài dlib từ wheel file (dễ hơn)
pip install https://github.com/jloh02/dlib/releases/download/v19.22/dlib-19.22.99-cp38-cp38-win_amd64.whl
pip install face-recognition
```

### 4. Cấu hình

Mở file `app.py` và cập nhật cấu hình nếu cần:

```python
MONGODB_URI = "mongodb://localhost:27017/"  # Hoặc MongoDB Atlas URI
DATABASE_NAME = "face_recognition_db"
FACE_MATCH_THRESHOLD = 0.6  # Ngưỡng nhận diện (thấp hơn = nghiêm ngặt hơn)
```

## 🎮 Chạy ứng dụng

```bash
python app.py
```

Ứng dụng sẽ chạy tại:
- **Frontend**: http://localhost:5000
- **API Docs**: http://localhost:5000/api/docs

## 📖 Hướng dẫn sử dụng

### 1. Đăng ký người dùng mới

1. Truy cập http://localhost:5000/register
2. Cho phép truy cập camera
3. Chụp ảnh khuôn mặt (đảm bảo khuôn mặt rõ ràng)
4. Nhập họ tên và mã số
5. Nhấn "Đăng ký"

### 2. Nhận diện khuôn mặt

1. Truy cập http://localhost:5000/recognize
2. Nhấn "Bắt đầu nhận diện"
3. Hệ thống sẽ tự động:
   - Phát hiện khuôn mặt
   - Nhận diện người dùng
   - Vẽ khung và tên trên video
   - Ghi điểm danh

### 3. Xem điểm danh

1. Truy cập http://localhost:5000/attendance
2. Xem lịch sử điểm danh
3. Lọc theo ngày
4. Làm mới dữ liệu

## 🔌 API Endpoints

### POST /api/register
Đăng ký người dùng mới

**Form Data:**
- `name`: Họ và tên
- `user_id`: Mã số
- `image`: File ảnh

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user_id": "123"
}
```

### POST /api/recognize
Nhận diện khuôn mặt từ ảnh

**Form Data:**
- `image`: File ảnh/frame

**Response:**
```json
{
  "faces": [
    {
      "top": 100,
      "right": 300,
      "bottom": 400,
      "left": 200,
      "name": "Nguyen Van A",
      "confidence": 0.95
    }
  ],
  "timestamp": "2026-01-28T17:30:00"
}
```

### GET /api/users
Lấy danh sách người dùng

### GET /api/attendance
Lấy lịch sử điểm danh

### GET /api/stats
Lấy thống kê hệ thống

## 🛠️ Cấu trúc thư mục

```
face/
├── app.py                 # Ứng dụng chính (Flask + FastAPI)
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html         # Template cơ sở
│   ├── index.html        # Dashboard
│   ├── register.html     # Trang đăng ký
│   ├── recognize.html    # Trang nhận diện
│   └── attendance.html   # Trang điểm danh
└── README.md            # Tài liệu này
```

## 🎨 Công nghệ sử dụng

- **Backend Framework**: Flask, FastAPI
- **Face Recognition**: face_recognition (dlib)
- **Database**: MongoDB (pymongo)
- **Frontend**: HTML5, CSS3, JavaScript
- **Face Visualization**: face-api.js
- **Image Processing**: OpenCV, Pillow

## ⚙️ Tùy chỉnh

### Thay đổi ngưỡng nhận diện

Trong `app.py`, điều chỉnh:
```python
FACE_MATCH_THRESHOLD = 0.6  # 0.0 - 1.0 (thấp hơn = nghiêm ngặt hơn)
```

### Thay đổi tần suất nhận diện

Trong `templates/recognize.html`, điều chỉnh:
```javascript
recognitionInterval = setInterval(recognizeFrame, 1000); // milliseconds
```

## 🐛 Xử lý lỗi thường gặp

### Lỗi: "No face detected"
- Đảm bảo ánh sáng đủ
- Khuôn mặt nhìn thẳng vào camera
- Không bị che khuất

### Lỗi: "Cannot connect to MongoDB"
- Kiểm tra MongoDB service đang chạy
- Kiểm tra connection string
- Kiểm tra firewall

### Lỗi: "Camera not accessible"
- Cho phép truy cập camera trong browser
- Kiểm tra camera không bị ứng dụng khác sử dụng
- Sử dụng HTTPS hoặc localhost

## 📝 License

MIT License - Tự do sử dụng cho mục đích cá nhân và thương mại.

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Hãy tạo issue hoặc pull request.

## 📧 Liên hệ

Nếu có thắc mắc, vui lòng tạo issue trên GitHub.

---

Made with ❤️ using Python, MongoDB, and face-api.js
