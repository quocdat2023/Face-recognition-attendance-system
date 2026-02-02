# 📸 Hệ Thống Điểm Danh Khuôn Mặt Thông Minh (Smart Face Attendance)

Hệ thống điểm danh tự động sử dụng công nghệ nhận diện khuôn mặt (Face Recognition) kết hợp với các thuật toán chống giả mạo (Anti-Spoofing) để đảm bảo tính xác thực và bảo mật.

## 🚀 Tính Năng Nổi Bật

- **Nhận diện khuôn mặt chính xác**: Sử dụng thư viện `face_recognition` (dlib) với độ chính xác cao.
- **🛡️ Chống giả mạo (Anti-Spoofing) 3 Lớp**:
  1.  **Chống ảnh mờ (Blur Check)**: Loại bỏ các hình ảnh chất lượng thấp hoặc quay lén.
  2.  **Chống lóa (Glare Check)**: Phát hiện và chặn việc sử dụng màn hình điện thoại hoặc ảnh in giấy bóng để qua mặt hệ thống.
  3.  **Phát hiện Moiré (Screen Pattern)**: Phân tích tần số để cảnh báo khi phát hiện lưới pixel (chụp lại màn hình).
- **Quản lý Ca làm việc**: Hỗ trợ điểm danh theo 4 ca linh hoạt trong ngày.
- **Kiểm soát ngày**: Chỉ cho phép điểm danh vào các ngày quy định (Thứ 2, 4, 6 - có thể cấu hình).
- **Lưu trữ dữ liệu**: Sử dụng MongoDB để lưu trữ thông tin nhân viên và lịch sử điểm danh.
- **Giao diện hiện đại**: Frontend HTML5/CSS3 thân thiện, tích hợp camera trực tiếp.

## 🛠️ Công Nghệ Sử Dụng

- **Backend API**: FastAPI (High performance)
- **Frontend App**: Flask (Jinja2 Templates)
- **Computer Vision**: OpenCV, Face Recognition, NumPy
- **Database**: MongoDB
- **Containerization**: Docker, Docker Compose

---

## ⚙️ Cài Đặt & Chạy (Local)

### Yêu cầu
- Python 3.8 trở lên
- MongoDB (đã cài đặt và đang chạy)
- CMake (để build thư viện dlib)

### Bước 1: Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### Bước 2: Chạy ứng dụng
```bash
python app.py
```
Truy cập: [http://localhost:5000](http://localhost:5000)

---

## 🐳 Cài Đặt & Chạy (Docker) - Khuyên Dùng

Nếu bạn không muốn cài đặt Python/Mongo thủ công, hãy sử dụng Docker.

### Bước 1: Build và Run
Mở terminal tại thư mục dự án và chạy:
```bash
docker-compose up --build
```

### Bước 2: Sử dụng
Hệ thống sẽ tự động khởi tạo MongoDB và Web Server.
- Web UI: [http://localhost:5000](http://localhost:5000)
- MongoDB Database: `mongodb://localhost:27017`

---

## 📂 Cấu Trúc Dự Án

```
face_attendance/
├── app.py                 # File chính (Flask + FastAPI config)
├── liveness_analysis.py   # Module bảo mật (Anti-Spoofing logic)
├── requirements.txt       # Danh sách thư viện
├── Dockerfile             # Cấu hình Docker image
├── docker-compose.yml     # Cấu hình Docker services
├── templates/             # Giao diện HTML
│   ├── index.html
│   ├── register.html
│   ├── recognize.html
│   └── ...
└── README.md              # Tài liệu hướng dẫn
```

## ⚠️ Lưu Ý Bảo Mật
File `liveness_analysis.py` chứa các ngưỡng (threshold) để phát hiện giả mạo. Tùy thuộc vào chất lượng Camera của bạn, bạn có thể cần điều chỉnh các thông số:
- `BLUR_THRESHOLD`: Tăng nếu muốn chặn ảnh mờ gắt gao hơn.
- `MOIRE_THRESHOLD`: Điều chỉnh độ nhạy với màn hình điện tử.

---
**Phát triển bởi [Tên Bạn]**
