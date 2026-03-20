# Simple Books Management API

API quản lý sách đơn giản viết bằng Flask với Swagger UI.

## Mô tả

Đây là ứng dụng Flask cung cấp các endpoint để quản lý danh sách sách:
- **GET /books** - Lấy danh sách tất cả sách
- **POST /books** - Tạo sách mới
- **GET /books/{id}** - Lấy chi tiết sách theo ID
- **PUT /books/{id}** - Cập nhật thông tin sách
- **DELETE /books/{id}** - Xóa sách

## Cài đặt

### 1. Tạo virtual environment
```bash
python -m venv venv
```

### 2. Kích hoạt virtual environment
**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
python app.py
```

Server sẽ khởi động tại `http://localhost:5000`

## Truy cập API

### API Home Page
```
http://localhost:5000/
```

### Swagger UI (Interactive API Documentation)
```
http://localhost:5000/api/docs
```

Tại đây, bạn có thể:
- Xem tài liệu API
- Thử gọi các endpoint trực tiếp
- Xem request/response examples
- Tạo và kiểm tra các request

### OpenAPI Specification (JSON)
```
http://localhost:5000/openapi.json
```

## Ví dụ sử dụng API

### 1. Lấy danh sách sách
```bash
curl http://localhost:5000/books
```

**Response:**
```json
[
  {
    "id": "1",
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "publishedYear": 2008,
    "genre": "Software Engineering"
  },
  ...
]
```

### 2. Tạo sách mới
```bash
curl -X POST http://localhost:5000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Architecture",
    "author": "Robert C. Martin",
    "publishedYear": 2017,
    "genre": "Software Architecture"
  }'
```

**Response:**
```json
{
  "id": "4",
  "title": "Clean Architecture",
  "author": "Robert C. Martin",
  "publishedYear": 2017,
  "genre": "Software Architecture"
}
```

### 3. Lấy chi tiết sách theo ID
```bash
curl http://localhost:5000/books/1
```

### 4. Cập nhật sách
```bash
curl -X PUT http://localhost:5000/books/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code (Updated)",
    "author": "Robert C. Martin",
    "publishedYear": 2008,
    "genre": "Software Engineering"
  }'
```

### 5. Xóa sách
```bash
curl -X DELETE http://localhost:5000/books/1
```

## Cấu trúc tệp

```
├── app.py                 # Flask application
├── openapi.yml            # OpenAPI specification
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Technologies

- **Flask** - Lightweight Python web framework
- **Flasgger** - Flask + Swagger UI integration
- **Flask-CORS** - Handle Cross-Origin Resource Sharing
- **OpenAPI 3.0.3** - API specification standard

## Ghi chú

- API sử dụng bộ nhớ trong (in-memory) để lưu trữ dữ liệu
- Dữ liệu sẽ mất khi khởi động lại server
- Hiện tại có 3 sách mẫu được tải sẵn khi khởi động

## Tác giả

Bài tập tuần 3 - Kiến trúc hướng dịch vụ
