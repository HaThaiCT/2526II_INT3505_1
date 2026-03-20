# Client-Server - REST API Principle

## Mô tả

Nguyên lý **Client-Server** tách biệt concerns giữa client và server, cho phép chúng phát triển độc lập. Server cung cấp API (business logic, data), Client tiêu thụ API (UI, user interaction).

## Đặc điểm chính

- ✅ Tách biệt client và server
- ✅ Server: Cung cấp API, quản lý data, xử lý business logic
- ✅ Client: Hiển thị UI, gọi API, xử lý user interaction
- ✅ Giao tiếp qua HTTP/JSON
- ✅ Client và Server phát triển độc lập
- ✅ Một API phục vụ nhiều loại client (web, mobile, desktop)

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy server

```bash
python app.py
```

Server sẽ chạy tại: http://localhost:5004

## Kiến trúc

```
┌─────────────────┐         HTTP/JSON        ┌──────────────────┐
│                 │    ←─────────────────→    │                  │
│  CLIENT         │                           │   SERVER (API)   │
│  (Postman/Web)  │    GET/POST/PUT/DELETE    │                  │
│                 │                           │                  │
│  - UI           │                           │  - Business      │
│  - Rendering    │                           │    Logic         │
│  - User Input   │                           │  - Database      │
│                 │                           │  - Validation    │
└─────────────────┘                           └──────────────────┘
```

## Test với Postman

### 1. GET - Lấy tất cả tasks

**Request:**
```
Method: GET
URL: http://localhost:5004/api/tasks
```

**Response (200 OK):**
```json
{
  "success": true,
  "count": 3,
  "data": [
    {
      "id": 1,
      "title": "Học Flask",
      "description": "Tìm hiểu về Flask framework",
      "completed": false,
      "priority": "high"
    },
    {
      "id": 2,
      "title": "Học REST API",
      "description": "Nắm vững các nguyên lý REST",
      "completed": true,
      "priority": "high"
    }
  ]
}
```

### 2. GET - Filter tasks

**Lấy tasks chưa hoàn thành:**
```
Method: GET
URL: http://localhost:5004/api/tasks?completed=false
```

**Lấy tasks có priority cao:**
```
Method: GET
URL: http://localhost:5004/api/tasks?priority=high
```

**Response (200 OK):**
```json
{
  "success": true,
  "count": 1,
  "data": [...]
}
```

### 3. GET - Lấy task theo ID

**Request:**
```
Method: GET
URL: http://localhost:5004/api/tasks/1
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Học Flask",
    "description": "Tìm hiểu về Flask framework",
    "completed": false,
    "priority": "high"
  }
}
```

### 4. POST - Tạo task mới

**Request:**
```
Method: POST
URL: http://localhost:5004/api/tasks
Headers: Content-Type: application/json
Body (raw JSON):
{
  "title": "Học Docker",
  "description": "Containerization với Docker",
  "priority": "high"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Task created successfully",
  "data": {
    "id": 4,
    "title": "Học Docker",
    "description": "Containerization với Docker",
    "completed": false,
    "priority": "high"
  }
}
```

### 5. PUT - Cập nhật task

**Request:**
```
Method: PUT
URL: http://localhost:5004/api/tasks/1
Headers: Content-Type: application/json
Body (raw JSON):
{
  "title": "Học Flask (Updated)",
  "completed": true,
  "priority": "high"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Task updated successfully",
  "data": {
    "id": 1,
    "title": "Học Flask (Updated)",
    "description": "Tìm hiểu về Flask framework",
    "completed": true,
    "priority": "high"
  }
}
```

### 6. DELETE - Xóa task

**Request:**
```
Method: DELETE
URL: http://localhost:5004/api/tasks/1
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

### 7. GET - Lấy categories

**Request:**
```
Method: GET
URL: http://localhost:5004/api/categories
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": ["Work", "Study", "Personal", "Shopping"]
}
```

### 8. GET - Thống kê tasks

**Request:**
```
Method: GET
URL: http://localhost:5004/api/stats
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "total_tasks": 3,
    "completed_tasks": 1,
    "pending_tasks": 2,
    "completion_rate": 33.33,
    "priority_breakdown": {
      "high": 2,
      "medium": 1,
      "low": 0
    }
  }
}
```

## Phân biệt trách nhiệm

### Server (Backend) - `app.py`

**Trách nhiệm:**
- ✅ Quản lý database (lưu trữ tasks)
- ✅ Xử lý business logic (tính toán stats, filter)
- ✅ Validate dữ liệu (check required fields)
- ✅ Cung cấp JSON API
- ✅ Xử lý errors

**Không làm:**
- ❌ Hiển thị UI
- ❌ Xử lý CSS/HTML
- ❌ Handle user clicks

### Client (Frontend/Postman)

**Trách nhiệm:**
- ✅ Hiển thị UI/interface
- ✅ Gọi API khi cần data
- ✅ Render data từ API
- ✅ Handle user interaction (clicks, inputs)
- ✅ Client-side validation (UX)

**Không làm:**
- ❌ Lưu trữ data (chỉ cache tạm)
- ❌ Business logic phức tạp
- ❌ Direct database access

## Lợi ích của Client-Server

### 1. Phát triển độc lập
- Frontend team và Backend team làm việc song song
- Chỉ cần thống nhất API contract

### 2. Một API, nhiều client
```
                    ┌─> Web App (React)
                    │
Server API ─────────┼─> Mobile App (iOS)
                    │
                    ├─> Mobile App (Android)
                    │
                    └─> Desktop App (Electron)
```

### 3. Dễ scale
- Scale server và client riêng biệt
- Thêm server khi traffic cao
- Update UI không ảnh hưởng backend

### 4. Bảo mật tốt hơn
- Business logic và data nằm ở server
- Client không truy cập trực tiếp database
- Validate ở cả client (UX) và server (security)

### 5. Dễ maintain
- Thay đổi UI không cần sửa backend
- Thay đổi business logic không cần sửa UI
- Code separation rõ ràng

## Workflow Example

**User muốn tạo task mới:**

1. **Client (Postman/Web):**
   - User nhập title, description
   - Click "Create"
   - Client gửi POST request với JSON data

2. **Server (Flask API):**
   - Nhận request
   - Validate: title có rỗng không?
   - Business logic: tạo ID mới, set defaults
   - Lưu vào database
   - Trả về JSON response

3. **Client:**
   - Nhận response
   - Hiển thị task mới trong UI
   - Show success message

## Test Workflow với Postman

**Scenario: Quản lý tasks**

1. ✅ GET `/api/tasks` - Xem tất cả tasks
2. ✅ POST `/api/tasks` - Tạo task mới "Học Kubernetes"
3. ✅ GET `/api/tasks` - Xác nhận task mới xuất hiện
4. ✅ PUT `/api/tasks/4` - Đánh dấu hoàn thành
5. ✅ GET `/api/stats` - Xem thống kê cập nhật
6. ✅ DELETE `/api/tasks/4` - Xóa task
7. ✅ GET `/api/tasks` - Xác nhận đã xóa

## CORS (Cross-Origin Resource Sharing)

API này bật CORS (`Flask-CORS`) để cho phép:
- Web clients từ different origins truy cập API
- Postman, mobile apps gọi API không bị block
- Frontend (localhost:3000) gọi Backend (localhost:5004)

## Tóm tắt

| Aspect | Client | Server |
|--------|--------|--------|
| **Data** | Temporary (cache) | Persistent (database) |
| **Logic** | UI logic | Business logic |
| **Language** | Any (JS, Swift, Kotlin) | Python (Flask) |
| **Output** | Visual UI | JSON data |
| **Dependency** | Depends on Server API | Independent |

**Key Point:** Client và Server giao tiếp QUA API (HTTP/JSON), hoàn toàn độc lập về implementation!
