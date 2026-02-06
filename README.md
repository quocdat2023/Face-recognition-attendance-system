# 👤 Face Recognition Attendance System

Hệ thống nhận diện khuôn mặt và điểm danh tự động thông minh, tích hợp lưu trữ ảnh trên Cloudinary và cơ sở dữ liệu MongoDB.

## ✨ Tính năng nổi bật

- 📝 **Đăng ký thông minh**: Thu thập 10 ảnh mẫu nhìn thẳng, tự động tạo vector nhận diện.
- ☁️ **Lưu trữ Cloudinary**: Tự động upload ảnh đại diện người dùng và ảnh chụp lúc điểm danh lên Cloud (không tốn dung lượng server).
- 🎯 **Nhận diện chính xác**: Sử dụng mô hình Deep Learning (face_recognition & dlib) để nhận diện với độ chính xác cao.
- ✅ **Điểm danh theo ca**: Hỗ trợ 4 ca làm việc/ngày, kiểm tra trùng lặp, chỉ cho phép điểm danh vào Thứ 2, 4, 6.
- 👥 **Quản lý người dùng**: Xem danh sách, xem ảnh đại diện phóng to, xóa người dùng.
- 📊 **Lịch sử & Thống kê**: Xem lịch sử điểm danh kèm ảnh bằng chứng, thống kê theo ca, lọc theo ngày/ca.
- 🗑️ **Quản lý dữ liệu**: Xóa từng bản ghi hoặc xóa toàn bộ lịch sử điểm danh.
- 🎨 **Giao diện hiện đại**: Thiết kế Dark Mode, Responsive, hiệu ứng mượt mà.

## 🏗️ Kiến trúc hệ thống

- **Backend**: Python (Flask + FastAPI).
- **Database**: MongoDB (Lưu thông tin user, vector khuôn mặt, lịch sử điểm danh).
- **Storage**: Cloudinary (Lưu ảnh đăng ký và ảnh điểm danh).
- **AI/ML**: `face_recognition` (Python) cho xử lý backend, `face-api.js` cho trải nghiệm realtime frontend.
- **Frontend**: HTML5, CSS3, JavaScript.

## 📋 Yêu cầu hệ thống

- Python 3.8+
- MongoDB (Local hoặc Atlas)
- Tài khoản Cloudinary (Miễn phí)
- Webcam
- Visual Studio Build Tools (để cài đặt thư viện dlib trên Windows)

## 🚀 Cài đặt & Chạy ứng dụng

### 1. Clone project
```bash
git clone <repository-url>
cd Face-recognition-attendance-system
```

### 2. Cài đặt Python dependencies
```bash
pip install -r requirements.txt
```
*Lưu ý: Nếu gặp lỗi cài đặt `dlib`, hãy đảm bảo bạn đã cài Visual Studio Build Tools với "Desktop development with C++".*

### 3. Cấu hình môi trường (.env)
Tạo file `.env` tại thư mục gốc và điền thông tin cấu hình (xem `.env.example`):

```env
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
DB_NAME=face_recognition_db

# Cloudinary Configuration (Lấy từ Dashboard của Cloudinary)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### 4. Chạy ứng dụng
```bash
python app.py
```
Hệ thống sẽ khởi động tại: **http://localhost:5000**

## 📖 Hướng dẫn sử dụng

### 1. Đăng ký người dùng (Register)
- Truy cập menu **Đăng ký**.
- Nhập **Họ tên** và **Mã số**.
- Hệ thống yêu cầu chụp **10 ảnh** nhìn thẳng vào camera.
- Nhấn **Bắt đầu** để chụp tự động.
- Sau khi đủ ảnh, nhấn **Đăng ký**. Ảnh sẽ được upload lên Cloudinary và tạo dữ liệu nhận diện.

### 2. Quản lý người dùng (Users)
- Truy cập menu **Người dùng**.
- Xem danh sách tất cả nhân viên/sinh viên đã đăng ký.
- Click vào ảnh đại diện (avatar) để xem ảnh lớn.
- Nhấn nút **Xóa** để xóa người dùng khỏi hệ thống.

### 3. Điểm danh (Recognize)
- Truy cập menu **Nhận diện**.
- Chọn **Ngày** và **Ca làm việc** (Hệ thống tự động phát hiện Thứ 2, 4, 6).
- Nhấn **Bắt đầu điểm danh**.
- Camera sẽ quét và nhận diện khuôn mặt. Nếu trùng khớp, hệ thống sẽ:
  - Hiển thị tên và độ tin cậy.
  - Lưu bản ghi điểm danh vào MongoDB.
  - Chụp ảnh bằng chứng và upload lên Cloudinary.

### 4. Xem lịch sử (Attendance)
- Truy cập menu **Điểm danh**.
- Xem bảng thống kê số lượng điểm danh theo ca.
- Dưới bảng chi tiết, có thể click vào ảnh thumb để xem ảnh bằng chứng rõ nét.
- Sử dụng bộ lọc theo Ngày và Ca trực.
- Sử dụng nút **Xóa tất cả** hoặc xóa từng dòng để quản lý dữ liệu.

## 🛠️ Cấu trúc thư mục

```
Face-recognition-attendance-system/
├── app.py                 # Backend chính (Flask + FastAPI)
├── requirements.txt       # Các thư viện cần thiết
├── .env                   # Biến môi trường (User tự tạo)
├── templates/             # Giao diện Frontend
│   ├── base.html          # Layout chung
│   ├── index.html         # Trang chủ
│   ├── register.html      # Trang đăng ký (Logic chụp 10 ảnh)
│   ├── users.html         # Trang quản lý người dùng
│   ├── recognize.html     # Trang nhận diện/điểm danh
│   └── attendance.html    # Trang lịch sử điểm danh
└── README.md              # Hướng dẫn sử dụng
```

## 🐛 Xử lý sự cố thường gặp

1. **Lỗi `ImportError` liên quan đến `bson`**:
   - Chạy lệnh: `pip uninstall bson pymongo` sau đó `pip install pymongo`.

2. **Không kết nối được MongoDB**:
   - Kiểm tra xem MongoDB Service đã chạy chưa.
   - Kiểm tra `MONGO_URI` trong file `.env`.

3. **Lỗi upload Cloudinary**:
   - Kiểm tra lại `CLOUDINARY_CLOUD_NAME`, `API_KEY`, `API_SECRET` trong file `.env`.
   - Đảm bảo kết nối mạng ổn định.

## 📝 License
Dự án được xây dựng cho mục đích học tập và nghiên cứu.
