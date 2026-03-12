# Flask REST API - Homework Week 2

## Cài đặt
```bash
pip install -r requirements.txt
python app.py
```

## API Endpoints

### 1. Đăng nhập
```bash
POST /login
Body: {"username": "admin", "password": "123456"}
Response: {"token": "TOKEN_...", "user": {...}}
```

### 2. Lấy danh sách user (phân trang)
```bash
GET /users?page=1&limit=10
Header: Authorization: Bearer TOKEN_...
Response: {"data": [...], "page": 1, "limit": 10, "total": 2}
```

### 3. Tạo user mới
```bash
POST /users
Header: Authorization: Bearer TOKEN_...
Body: {"username": "user2", "email": "user2@test.com", "password": "123456"}
Response: {"id": 3, "username": "user2", "email": "user2@test.com"}
```

### 4. Cập nhật email
```bash
PUT /users/2/email
Header: Authorization: Bearer TOKEN_...
Body: {"email": "newemail@test.com"}
Response: {"id": 2, "username": "user1", "email": "newemail@test.com"}
```

### 5. Xóa user
```bash
DELETE /users/2
Header: Authorization: Bearer TOKEN_...
Response: {"message": "Đã xóa user"}
```

## Test với curl

```bash
# Đăng nhập
curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"123456\"}"

# Lưu token
TOKEN="TOKEN_admin_..."

# Lấy danh sách
curl http://localhost:5000/users -H "Authorization: Bearer $TOKEN"

# Tạo user
curl -X POST http://localhost:5000/users -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "{\"username\":\"user2\",\"email\":\"user2@test.com\",\"password\":\"123456\"}"

# Cập nhật email
curl -X PUT http://localhost:5000/users/2/email -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "{\"email\":\"new@test.com\"}"

# Xóa user
curl -X DELETE http://localhost:5000/users/2 -H "Authorization: Bearer $TOKEN"
```

## Tài khoản mặc định
- Username: `admin`, Password: `123456`
- Username: `user1`, Password: `123456`
