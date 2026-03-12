# Stateless - REST API Principle

## Mô tả

Nguyên lý **Stateless** đảm bảo mỗi request chứa tất cả thông tin cần thiết để xử lý. Server không lưu trữ session hay trạng thái của client giữa các requests.

## Đặc điểm chính

- ✅ Mỗi request tự chứa đầy đủ thông tin (authentication token)
- ✅ Server không lưu session
- ✅ Sử dụng JWT (JSON Web Token) để xác thực
- ✅ Token chứa user info, không cần query database mỗi request
- ✅ Dễ scale horizontal (có thể thêm server mà không cần đồng bộ session)

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy server

```bash
python app.py
```

Server sẽ chạy tại: http://localhost:5002

## Test với Postman

### 1. POST - Login (lấy token)

**Request:**
```
Method: POST
URL: http://localhost:5002/api/login
Headers: Content-Type: application/json
Body (raw JSON):
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": "1 hour"
}
```

**➡️ Copy token này để dùng cho các requests tiếp theo**

### 2. GET - Profile (cần token)

**Request:**
```
Method: GET
URL: http://localhost:5002/api/profile
Headers: 
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Cách thêm token trong Postman:**
1. Chọn tab **Headers**
2. Key: `Authorization`
3. Value: `Bearer <paste_token_ở_đây>`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "username": "admin",
    "name": "Administrator",
    "role": "admin"
  }
}
```

### 3. GET - Products (cần token)

**Request:**
```
Method: GET
URL: http://localhost:5002/api/products
Headers: 
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "success": true,
  "user": "admin",
  "data": [
    {"id": 1, "name": "Laptop", "price": 1000},
    {"id": 2, "name": "Mouse", "price": 20},
    {"id": 3, "name": "Keyboard", "price": 50}
  ]
}
```

### 4. POST - Calculate (không cần token)

**Request:**
```
Method: POST
URL: http://localhost:5002/api/calculate
Headers: Content-Type: application/json
Body (raw JSON):
{
  "num1": 10,
  "num2": 5,
  "operation": "add"
}
```

**Operations hỗ trợ:** `add`, `subtract`, `multiply`, `divide`

**Response (200 OK):**
```json
{
  "success": true,
  "input": {
    "num1": 10,
    "num2": 5,
    "operation": "add"
  },
  "result": 15
}
```

## Test Error Cases

### Token không hợp lệ
```
Method: GET
URL: http://localhost:5002/api/profile
Headers: Authorization: Bearer invalid_token
```

**Response (401 Unauthorized):**
```json
{
  "success": false,
  "error": "Invalid token"
}
```

### Thiếu token
```
Method: GET
URL: http://localhost:5002/api/profile
(không có Authorization header)
```

**Response (401 Unauthorized):**
```json
{
  "success": false,
  "error": "Token is missing"
}
```

## Accounts để test

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | admin |
| user1 | user123 | user |

## Lợi ích của Stateless

1. **Scalability**: Dễ dàng scale horizontal (thêm server)
2. **Reliability**: Không lo mất session khi server restart
3. **Performance**: Không cần lưu/đọc session từ database
4. **Simplicity**: Server đơn giản hơn, không quản lý state
5. **Load Balancing**: Request nào cũng có thể xử lý bởi server nào

## Lưu ý

- Token có thời hạn (1 giờ trong ví dụ này)
- Trong production, cần bảo mật SECRET_KEY
- Nên sử dụng HTTPS để bảo vệ token
- Password nên được hash (bcrypt, argon2)
