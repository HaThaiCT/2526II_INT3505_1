# Phân tích mã lỗi HTTP

## 1. 200 OK
**Ý nghĩa:** Request thành công

**Khi nào dùng:**
- Lấy dữ liệu thành công (GET)
- Cập nhật thành công (PUT)
- Xóa thành công (DELETE)

**Ví dụ trong API:**
```json
GET /users
Response 200: {"data": [...], "page": 1, "total": 2}
```

---

## 2. 201 Created
**Ý nghĩa:** Tạo resource mới thành công

**Khi nào dùng:**
- Tạo user/resource mới (POST)

**Ví dụ trong API:**
```json
POST /users
Response 201: {"id": 3, "username": "user2", "email": "user2@test.com"}
```

---

## 3. 400 Bad Request
**Ý nghĩa:** Dữ liệu gửi lên không hợp lệ

**Khi nào dùng:**
- Thiếu field bắt buộc
- Format dữ liệu sai (email không hợp lệ)
- Giá trị không phù hợp (page < 1)
- Username đã tồn tại

**Ví dụ trong API:**
```json
POST /users (thiếu email)
Response 400: {"error": "Thiếu thông tin bắt buộc"}

POST /users (email sai format)
Response 400: {"error": "Email không hợp lệ"}

GET /users?page=0
Response 400: {"error": "page và limit phải > 0"}
```

---

## 4. 401 Unauthorized
**Ý nghĩa:** Chưa xác thực hoặc xác thực sai

**Khi nào dùng:**
- Không gửi token
- Token không hợp lệ
- Sai username/password khi login

**Ví dụ trong API:**
```json
GET /users (không có token)
Response 401: {"error": "Token không hợp lệ"}

POST /login (sai password)
Response 401: {"error": "Sai username hoặc password"}
```

---

## 5. 404 Not Found
**Ý nghĩa:** Không tìm thấy resource

**Khi nào dùng:**
- User ID không tồn tại
- Endpoint không tồn tại

**Ví dụ trong API:**
```json
PUT /users/999/email
Response 404: {"error": "Không tìm thấy user"}

DELETE /users/999
Response 404: {"error": "Không tìm thấy user"}
```

---

## 6. 429 Too Many Requests
**Ý nghĩa:** Gửi quá nhiều request trong thời gian ngắn

**Khi nào dùng:**
- Vượt quá rate limit
- Chống spam/DDoS

**Ví dụ trong API:**
```json
Response 429: {"error": "Quá nhiều request"}
```

**Cách implement:**
- Đếm số request per IP trong khoảng thời gian
- Giới hạn: 20 requests/phút, 100 requests/giờ...
- Lưu trong memory, Redis, hoặc database

---

## 7. 500 Internal Server Error
**Ý nghĩa:** Lỗi server không mong đợi

**Khi nào dùng:**
- Exception không được xử lý
- Database connection failed
- Lỗi code logic

**Ví dụ trong API:**
```json
Response 500: {"error": "Lỗi server"}
```

**Best practice:**
- Log chi tiết lỗi để debug
- Không expose stack trace cho client
- Trả về message chung chung

---

## So sánh 4xx vs 5xx

| Loại | Ý nghĩa | Trách nhiệm |
|------|---------|-------------|
| **4xx** | Lỗi từ phía client | Client sửa request |
| **5xx** | Lỗi từ phía server | Server fix bug |

**Ví dụ:**
- 400: Client gửi sai format → Client phải sửa
- 500: Server bị crash → Dev phải fix code

---

## Bảng tổng hợp

| Mã | Tên | Khi nào dùng | Ví dụ request |
|----|-----|--------------|---------------|
| **200** | OK | Thành công | GET, PUT, DELETE |
| **201** | Created | Tạo mới thành công | POST /users |
| **400** | Bad Request | Dữ liệu sai | Thiếu field, email sai |
| **401** | Unauthorized | Chưa đăng nhập | Không có token |
| **404** | Not Found | Không tìm thấy | User ID không tồn tại |
| **429** | Too Many Requests | Quá nhiều request | Vượt rate limit |
| **500** | Internal Server Error | Lỗi server | Exception, crash |

---

## Best Practices

1. **Luôn trả về JSON nhất quán:**
```json
{"error": "Mô tả lỗi"}
{"data": {...}}
```

2. **Thêm message rõ ràng:**
```json
{"error": "Email không hợp lệ"}
```
Thay vì:
```json
{"error": "Invalid input"}
```

3. **Validation đầy đủ:**
- Check required fields
- Validate format (email, phone...)
- Check business rules (unique username...)

4. **Xử lý error đúng layer:**
- 400: Validation layer
- 401: Authentication layer
- 404: Data layer
- 500: Try-catch bao ngoài
