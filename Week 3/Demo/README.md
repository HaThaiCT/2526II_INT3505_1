# REST API Architecture Principles - Flask Examples

Các ví dụ minh họa **4 nguyên lý kiến trúc REST API** sử dụng Flask framework, được tổ chức thành các folder riêng biệt để dễ học và test.

## 📁 Cấu trúc thư mục

```
Week 2/Demo/
├── 1_uniform_interface/    # Uniform Interface principle
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
│
├── 2_stateless/            # Stateless principle
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
│
├── 3_cacheable/            # Cacheable principle
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
│
├── 4_client_server/        # Client-Server principle
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
│
└── README.md              # File này
```

## 🚀 Cài đặt nhanh

### Cách 1: Cài đặt từng folder

```bash
# Di chuyển vào folder
cd "1_uniform_interface"

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server
python app.py
```

### Cách 2: Cài đặt tất cả cùng lúc

```bash
# Từ folder Demo
pip install Flask Flask-CORS PyJWT
```

## 📚 4 Nguyên lý REST API

### 1️⃣ Uniform Interface (Giao diện thống nhất)

📂 **Folder:** `1_uniform_interface/`  
🌐 **Port:** 5001

**Khái niệm:**
- Sử dụng HTTP methods chuẩn (GET, POST, PUT, DELETE)
- URI có cấu trúc nhất quán
- Response format chuẩn (JSON)

**Test với Postman:**
- ✅ GET `/api/books` - Lấy danh sách
- ✅ POST `/api/books` - Tạo mới
- ✅ PUT `/api/books/:id` - Cập nhật
- ✅ DELETE `/api/books/:id` - Xóa

👉 [Xem hướng dẫn chi tiết](1_uniform_interface/README.md)

---

### 2️⃣ Stateless (Không trạng thái)

📂 **Folder:** `2_stateless/`  
🌐 **Port:** 5002

**Khái niệm:**
- Mỗi request tự chứa đủ thông tin (JWT token)
- Server không lưu session
- Dễ scale horizontal

**Test với Postman:**
- ✅ POST `/api/login` - Đăng nhập, nhận token
- ✅ GET `/api/profile` - Xem profile (cần token)
- ✅ GET `/api/products` - Lấy data (cần token)

**Test accounts:**
- Username: `admin` / Password: `admin123`
- Username: `user1` / Password: `user123`

👉 [Xem hướng dẫn chi tiết](2_stateless/README.md)

---

### 3️⃣ Cacheable (Có thể cache)

📂 **Folder:** `3_cacheable/`  
🌐 **Port:** 5003

**Khái niệm:**
- Sử dụng HTTP cache headers
- Cache-Control, Expires, ETag
- Tăng performance, giảm tải server

**Test với Postman:**
- ✅ GET `/api/products` - Cache 5 phút
- ✅ GET `/api/products/:id` - Cache 2 phút
- ✅ GET `/api/products/etag` - ETag validation
- ✅ GET `/api/products/no-cache` - Không cache

**Cách test cache:**
1. Gọi endpoint → note timestamp
2. Gọi lại → timestamp giống = cached
3. Check response headers: `Cache-Control`, `Expires`

👉 [Xem hướng dẫn chi tiết](3_cacheable/README.md)

---

### 4️⃣ Client-Server (Tách biệt Client-Server)

📂 **Folder:** `4_client_server/`  
🌐 **Port:** 5004

**Khái niệm:**
- Tách biệt frontend và backend
- Server: API, business logic, database
- Client: UI, user interaction
- Phát triển độc lập

**Test với Postman:**
- ✅ GET `/api/tasks` - Danh sách tasks
- ✅ POST `/api/tasks` - Tạo task mới
- ✅ PUT `/api/tasks/:id` - Cập nhật
- ✅ DELETE `/api/tasks/:id` - Xóa
- ✅ GET `/api/stats` - Thống kê

👉 [Xem hướng dẫn chi tiết](4_client_server/README.md)

---

## 🧪 Test với Postman

### Import nhanh:

Mỗi folder có hướng dẫn chi tiết về:
- ✅ Các endpoints cần test
- ✅ Request body mẫu (JSON)
- ✅ Expected responses
- ✅ Headers cần thiết
- ✅ Error cases

### Workflow học tập đề xuất:

1. **Đọc README** của từng folder
2. **Chạy server** trên terminal
3. **Mở Postman** và tạo requests
4. **Test từng endpoint** theo hướng dẫn
5. **Quan sát** responses và headers
6. **Thử error cases** (invalid data, missing token, etc.)

## 📊 So sánh các nguyên lý

| Nguyên lý | Port | Mục đích chính | Lợi ích |
|-----------|------|----------------|---------|
| **Uniform Interface** | 5001 | Chuẩn hóa API design | Dễ hiểu, tương thích, maintainable |
| **Stateless** | 5002 | Không lưu session | Scale tốt, reliability, simplicity |
| **Cacheable** | 5003 | Tối ưu performance | Nhanh hơn, tiết kiệm tài nguyên |
| **Client-Server** | 5004 | Tách concerns | Phát triển độc lập, reusable API |

## ⚡ Quick Start

```bash
# Terminal 1 - Uniform Interface
cd "1_uniform_interface"
pip install -r requirements.txt
python app.py

# Terminal 2 - Stateless
cd "2_stateless"
pip install -r requirements.txt
python app.py

# Terminal 3 - Cacheable
cd "3_cacheable"
pip install -r requirements.txt
python app.py

# Terminal 4 - Client-Server
cd "4_client_server"
pip install -r requirements.txt
python app.py
```

Sau đó mở Postman và test:
- 📘 http://localhost:5001 - Uniform Interface
- 📗 http://localhost:5002 - Stateless
- 📙 http://localhost:5003 - Cacheable
- 📕 http://localhost:5004 - Client-Server

## 💡 Tips

1. **Kiểm tra server đang chạy:**
   - Mở browser: http://localhost:5001 (hoặc 5002, 5003, 5004)
   - Sẽ thấy API documentation

2. **Test với Postman:**
   - Tạo Collection riêng cho từng principle
   - Save requests để test lại sau
   - Sử dụng Environment variables cho base URL

3. **Debug:**
   - Check terminal logs khi gọi API
   - Response có field `success` để check lỗi
   - Status codes: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 404 (Not Found)

## 📖 Tài liệu thêm

Chi tiết về từng nguyên lý xem trong README.md của mỗi folder:
- [1_uniform_interface/README.md](1_uniform_interface/README.md)
- [2_stateless/README.md](2_stateless/README.md)
- [3_cacheable/README.md](3_cacheable/README.md)
- [4_client_server/README.md](4_client_server/README.md)

## 🎯 Mục tiêu học tập

Sau khi hoàn thành các ví dụ này, bạn sẽ hiểu:
- ✅ Tại sao REST API được thiết kế theo các nguyên lý này
- ✅ Cách implement từng nguyên lý trong thực tế
- ✅ Lợi ích của từng nguyên lý
- ✅ Cách test API với Postman
- ✅ HTTP methods, status codes, headers

---

**Happy Learning! 🚀**
