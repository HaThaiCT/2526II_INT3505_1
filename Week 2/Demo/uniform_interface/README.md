# Uniform Interface - REST API Principle

## Mô tả

Nguyên lý **Uniform Interface** đảm bảo API sử dụng các phương thức HTTP chuẩn và URI có cấu trúc nhất quán, giúp API dễ hiểu và dễ sử dụng.

## Đặc điểm chính

- ✅ Sử dụng HTTP methods đúng ngữ nghĩa:
  - **GET**: Lấy dữ liệu (không thay đổi state)
  - **POST**: Tạo mới resource
  - **PUT**: Cập nhật resource
  - **DELETE**: Xóa resource
  
- ✅ URI có cấu trúc rõ ràng và nhất quán:
  - Collection: `/api/books`
  - Single item: `/api/books/{id}`

- ✅ Response có định dạng chuẩn (JSON)
- ✅ Status codes chuẩn HTTP

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy server

```bash
python app.py
```

Server sẽ chạy tại: http://localhost:5001

## Test với Postman

### 1. GET - Lấy tất cả sách

**Request:**
```
Method: GET
URL: http://localhost:5001/api/books
```

**Response (200 OK):**
```json
{
  "success": true,
  "count": 3,
  "data": [
    {
      "id": 1,
      "title": "Python Programming",
      "author": "John Doe",
      "year": 2020
    }
  ]
}
```

### 2. GET - Lấy sách theo ID

**Request:**
```
Method: GET
URL: http://localhost:5001/api/books/1
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Python Programming",
    "author": "John Doe",
    "year": 2020
  }
}
```

### 3. POST - Tạo sách mới

**Request:**
```
Method: POST
URL: http://localhost:5001/api/books
Headers: Content-Type: application/json
Body (raw JSON):
{
  "title": "Learning REST API",
  "author": "Nguyen Van A",
  "year": 2024
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Book created successfully",
  "data": {
    "id": 4,
    "title": "Learning REST API",
    "author": "Nguyen Van A",
    "year": 2024
  }
}
```

### 4. PUT - Cập nhật sách

**Request:**
```
Method: PUT
URL: http://localhost:5001/api/books/1
Headers: Content-Type: application/json
Body (raw JSON):
{
  "title": "Python Programming (Updated)",
  "author": "John Doe",
  "year": 2025
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Book updated successfully",
  "data": {
    "id": 1,
    "title": "Python Programming (Updated)",
    "author": "John Doe",
    "year": 2025
  }
}
```

### 5. DELETE - Xóa sách

**Request:**
```
Method: DELETE
URL: http://localhost:5001/api/books/1
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Book deleted successfully",
  "data": {
    "id": 1,
    "title": "Python Programming (Updated)",
    "author": "John Doe",
    "year": 2025
  }
}
```

## Postman Collection

Import vào Postman để test nhanh:

1. Mở Postman
2. Click **Import** > **Raw text**
3. Copy và paste các request URLs trên
4. Hoặc tạo collection mới với các request như hướng dẫn

## Lợi ích của Uniform Interface

1. **Dễ hiểu**: Developer nào cũng biết GET để lấy, POST để tạo
2. **Tương thích**: Hoạt động với mọi HTTP client
3. **Chuẩn hóa**: Tuân thủ HTTP standards
4. **Dễ bảo trì**: Cấu trúc rõ ràng, nhất quán
