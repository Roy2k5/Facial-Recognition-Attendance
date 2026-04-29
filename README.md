# 🎯 Hệ Thống Điểm Danh Nhận Diện Khuôn Mặt

Hệ thống điểm danh tự động sử dụng công nghệ nhận diện khuôn mặt với **InsightFace** và **FAISS** để quản lý chấm công nhân viên hiệu quả, nhanh chóng và chính xác.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)![InsightFace](https://img.shields.io/badge/InsightFace-0.7.3-orange.svg)![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Mục Lục

- [Giới Thiệu](#-giới-thiệu)
- [Công Nghệ Sử Dụng](#-công-nghệ-sử-dụng)
- [Kiến Trúc Hệ Thống](#-kiến-trúc-hệ-thống)
- [Cài Đặt](#-cài-đặt)
- [Hướng Dẫn Sử Dụng](#-hướng-dẫn-sử-dụng)
- [API Documentation](#-api-documentation)
- [Cấu Trúc Thư Mục](#-cấu-trúc-thư-mục)
- [Demo](#-demo)
- [Tương lai](#-tương-lai)
- [Đóng Góp](#-đóng-góp)
- [License](#-license)

---

## 🚀 Giới Thiệu

Hệ thống điểm danh nhận diện khuôn mặt là giải pháp tự động hóa quy trình chấm công, giúp:
- ✅ Giảm gian lận thời gian làm việc
- ✅ Tăng tốc độ điểm danh (< 2 giây/người)
- ✅ Quản lý dữ liệu tập trung, dễ dàng tra cứu
- ✅ Không cần thiết bị chuyên dụng (chỉ cần webcam)

---

## 🛠️ Công Nghệ Sử Dụng

- **InsightFace** ⭐ - Mô hình nhận diện khuôn mặt SOTA (State-of-the-Art)
  - Model: `buffalo_l` (độ chính xác cao)
  - Trích xuất embedding 512 chiều
  - Hỗ trợ GPU để tăng tốc

- **FAISS** ⭐ - Vector similarity search của Facebook AI
  - Tìm kiếm nearest neighbor siêu nhanh
  - Hỗ trợ hàng triệu vectors
  - Sử dụng IndexFlatL2 (L2 distance)


---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────┐
│   Browser   │
│  (Frontend) │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────┐
│   FastAPI Server    │
│  ┌───────────────┐  │
│  │   Routes      │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │   Services    │  │
│  │ ┌───────────┐ │  │
│  │ │InsightFace│ │  │ ← Trích xuất embedding
│  │ └───────────┘ │  │
│  │ ┌───────────┐ │  │
│  │ │   FAISS   │ │  │ ← Tìm kiếm vector
│  │ └───────────┘ │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │   Database    │  │ ← SQLite
│  └───────────────┘  │
└─────────────────────┘
```

### Luồng Xử Lý Điểm Danh

```
1. Webcam capture → 2. Gửi ảnh lên server
                     ↓
3. InsightFace trích xuất embedding (512-D vector)
                     ↓
4. FAISS tìm kiếm nearest neighbor trong index
                     ↓
5. Tính cosine similarity
                     ↓
6. So sánh với threshold
                     ↓
7. Lưu vào database nếu pass
                     ↓
8. Trả kết quả về frontend
```

---

## 📦 Cài Đặt

### Yêu Cầu Hệ Thống

- **Python**: 3.10 trở lên
- **RAM**: Tối thiểu 4GB 
- **GPU**: Không bắt buộc (có GPU NVIDIA sẽ nhanh hơn)
- **Webcam**: Độ phân giải tối thiểu 720p

### Bước 1: Clone Repository

```bash
git clone https://github.com/yourusername/FacialRecognitionAttendance.git
cd FacialRecognitionAttendance
```

### Bước 2: Tạo Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài Đặt Dependencies

**Với CPU:**
```bash
cd backend
pip install -r requirements.txt
```

**Với GPU (NVIDIA CUDA):**
```bash
cd backend
pip install -r requirements.txt
pip uninstall onnxruntime faiss-cpu
pip install onnxruntime-gpu faiss-gpu
```

### Bước 4: Cấu Hình

Tạo file `.env` trong thư mục `backend`:

```env
# App Config
APP_NAME=Facial Recognition Attendance
THRESHOLD=0.6
LOG_DIR=log

```

### Bước 5: Khởi Chạy Backend

```bash
cd backend
python app.py
```

Server sẽ chạy tại: `http://localhost:8000`

### Bước 6: Khởi Chạy Frontend

**Cách 1: Dùng Live Server (VS Code)**
- Cài extension "Live Server"
- Click chuột phải vào `frontend/index.html`
- Chọn "Open with Live Server"

**Cách 2: Mở trực tiếp file index.html**

---

## 📖 Hướng Dẫn Sử Dụng

### 1. Đăng Ký Nhân Viên Mới

1. Chuyển sang tab **"Đăng Ký"**
2. Nhập thông tin:
   - Họ và tên
   - Mã nhân viên (unique)
   - Chọn ảnh khuôn mặt (chính diện, rõ nét)
3. Click **"✓ Đăng Ký"**
4. Hệ thống sẽ:
   - Trích xuất đặc trưng khuôn mặt
   - Lưu vào database
   - Thêm vào FAISS index

### 2. Điểm Danh

1. Chuyển sang tab **"Điểm Danh"**
2. Cho phép truy cập webcam
3. Đưa khuôn mặt vào khung hình
4. Click **"📷 Chụp Ảnh"**
5. Hệ thống hiển thị kết quả:
   - ✅ Thành công: Tên, Mã NV, Độ chính xác
   - ❌ Thất bại: Lý do (không nhận diện được, độ tin cậy thấp, đã điểm danh)

### 3. Xem Lịch Sử

1. Chuyển sang tab **"Lịch Sử"**
2. Chọn ngày cần xem (mặc định: hôm nay)
3. Click **"🔍 Tìm"**
4. Xem danh sách điểm danh

### 4. Dashboard

- Xem tổng quan:
  - Tổng số nhân viên
  - Số người đã điểm danh hôm nay
  - Số người chưa điểm danh
- Xóa dữ liệu điểm danh hôm nay (nếu cần)

---

## 📚 API Documentation

**Swagger UI**: `http://localhost:8000/docs`

---

## 📁 Cấu Trúc Thư Mục

```
FacialRecognitionAttendance/
│
├── backend/
│   ├── core/                    # Core modules
│   │   ├── __init__.py
│   │   ├── config.py           # App configuration
│   │   └── logger.py           # Logging setup
│   │
│   ├── db/                      # Database
│   │   ├── __init__.py
│   │   └── database.py         # SQLAlchemy models
│   │
│   ├── routes/                  # API routes
│   │   ├── __init__.py
│   │   └── attendance.py       # Attendance endpoints
│   │
│   ├── schema/                  # Pydantic schemas
│   │   ├── __init__.py
│   │   └── user.py
│   │
│   ├── service/                 # Business logic
│   │   ├── __init__.py
│   │   ├── recognition_service.py  # InsightFace
│   │   └── faiss_service.py        # FAISS index
│   │
│   ├── middleware/              # Middlewares
│   │   ├── __init__.py
│   │   └── http.py             # Logging middleware
│   │
│   ├── app.py                   # Main application
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Environment variables
│
├── frontend/
│   ├── index.html              # Main HTML
│   ├── styles.css              # Styling
│   └── scripts.js              # JavaScript logic
│
├── uploads/                     # User photos
├── log/                         # Application logs
├── faiss_index.bin             # FAISS index file
├── attendance.db               # SQLite database
│
└── README.md                    # This file
```

---

## 🎬 Demo

![Demo1](demo/demo1.png)
![Demo2](demo/demo2.png)
![Demo3](demo/demo3.png)

## 🗺️ Tương Lai

- ⏳ Xuất báo cáo Excel/PDF
- ⏳ Quản lý ca làm việc
- ⏳ Email thông báo tự động
- ⏳ Tích hợp ứng dụng bên thứ ba

---

## 🤝 Đóng Góp

Hoan nghênh mọi đóng góp! 

---

📄 Giấy phép
Dự án này được cấp phép theo giấy phép MIT – xem tệp [LICENSE](LICENSE) để biết chi tiết.
---
🙏 Lời cảm ơn

- [InsightFace](https://github.com/deepinsight/insightface) - Face recognition model
- [FAISS](https://github.com/facebookresearch/faiss) - Vector similarity search
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework

---


<div align="center">

**⭐ Star repo này nếu bạn thấy hữu ích! ⭐**

</div>
