# Users & Orders API

## Cài đặt
```bash
pip install -r requirements.txt
python app.py
```

Server chạy tại: http://localhost:5000

## Users API

### GET /api/v1/users
Lấy danh sách tất cả users
```bash
curl http://localhost:5000/api/v1/users
```

### GET /api/v1/users/{id}
Lấy user theo ID
```bash
curl http://localhost:5000/api/v1/users/1
```

### POST /api/v1/users
Tạo user mới
```bash
curl -X POST http://localhost:5000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Lê Văn C","email":"c@test.com","age":28}'
```

### PUT /api/v1/users/{id}
Cập nhật user
```bash
curl -X PUT http://localhost:5000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Nguyễn Văn A Updated","age":26}'
```

### DELETE /api/v1/users/{id}
Xóa user
```bash
curl -X DELETE http://localhost:5000/api/v1/users/2
```

## Orders API

### GET /api/v1/orders
Lấy danh sách tất cả orders
```bash
curl http://localhost:5000/api/v1/orders
```

### GET /api/v1/orders/{id}
Lấy order theo ID
```bash
curl http://localhost:5000/api/v1/orders/1
```

### POST /api/v1/orders
Tạo order mới
```bash
curl -X POST http://localhost:5000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"product":"Keyboard","quantity":1,"total":50}'
```

### PUT /api/v1/orders/{id}
Cập nhật order
```bash
curl -X PUT http://localhost:5000/api/v1/orders/1 \
  -H "Content-Type: application/json" \
  -d '{"quantity":2,"total":2000}'
```

### DELETE /api/v1/orders/{id}
Xóa order
```bash
curl -X DELETE http://localhost:5000/api/v1/orders/2
```

## Dữ liệu mẫu

**Users:**
- ID 1: Nguyễn Văn A (a@test.com, 25 tuổi)
- ID 2: Trần Thị B (b@test.com, 30 tuổi)

**Orders:**
- ID 1: User 1, Laptop, 1 cái, $1000
- ID 2: User 2, Mouse, 2 cái, $40

## Response codes
- 200: Thành công (GET, PUT, DELETE)
- 201: Tạo mới thành công (POST)
- 400: Dữ liệu không hợp lệ
- 404: Không tìm thấy
