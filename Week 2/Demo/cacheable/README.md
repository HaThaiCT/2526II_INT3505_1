# Cacheable - REST API Principle

## Mô tả

Nguyên lý **Cacheable** cho phép response được cache để cải thiện hiệu suất, giảm tải server và giảm độ trễ cho client bằng cách sử dụng HTTP cache headers.

## Đặc điểm chính

- ✅ Sử dụng `Cache-Control` header
- ✅ Sử dụng `Expires` header
- ✅ Sử dụng `ETag` cho conditional requests
- ✅ Phân biệt public cache vs private cache
- ✅ Giảm số lượng requests đến server
- ✅ Tiết kiệm băng thông

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy server

```bash
python app.py
```

Server sẽ chạy tại: http://localhost:5003

## Test với Postman

### 1. GET - Products (cache 5 phút)

**Request:**
```
Method: GET
URL: http://localhost:5003/api/products
```

**Response (200 OK):**
```json
{
  "success": true,
  "cached_for": "5 minutes",
  "count": 4,
  "data": [...],
  "timestamp": "2024-03-06T10:30:00.123456"
}
```

**Headers để kiểm tra:**
- `Cache-Control: public, max-age=300`
- `Expires: Wed, 06 Mar 2024 10:35:00 GMT`
- `X-Generated-At: 2024-03-06T10:30:00.123456`

**Cách test cache trong Postman:**
1. Gọi endpoint lần đầu - xem timestamp
2. Gọi lại ngay lập tức - timestamp KHÔNG thay đổi (cached)
3. Đợi >5 phút - timestamp mới (cache hết hạn)

### 2. GET - Product by ID (cache 2 phút)

**Request:**
```
Method: GET
URL: http://localhost:5003/api/products/1
```

**Response (200 OK):**
```json
{
  "success": true,
  "cached_for": "2 minutes",
  "data": {
    "id": 1,
    "name": "Laptop Dell XPS",
    "price": 1500,
    "category": "Electronics"
  },
  "timestamp": "2024-03-06T10:30:00.123456"
}
```

**Headers:**
- `Cache-Control: public, max-age=120`

### 3. GET - Products No Cache

**Request:**
```
Method: GET
URL: http://localhost:5003/api/products/no-cache
```

**Response (200 OK):**
```json
{
  "success": true,
  "cached": false,
  "data": [...],
  "timestamp": "2024-03-06T10:30:00.123456"
}
```

**Headers:**
- `Cache-Control: no-cache, no-store, must-revalidate`
- `Pragma: no-cache`
- `Expires: 0`

**Test:** Mỗi lần gọi sẽ có timestamp mới (không cache)

### 4. GET - Products with ETag

**Request lần 1:**
```
Method: GET
URL: http://localhost:5003/api/products/etag
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [...],
  "timestamp": "2024-03-06T10:30:00.123456"
}
```

**Response Headers:**
- `ETag: "5d41402abc4b2a76b9719d911017c592"`
- `Cache-Control: public, max-age=60`

**Request lần 2 (với ETag):**
```
Method: GET
URL: http://localhost:5003/api/products/etag
Headers:
  If-None-Match: "5d41402abc4b2a76b9719d911017c592"
```

**Response (304 Not Modified) - No body**
- Server trả về 304 = dữ liệu không đổi
- Client dùng cached data
- Tiết kiệm băng thông!

**Cách test ETag trong Postman:**
1. Gọi `/api/products/etag` lần đầu
2. Copy giá trị `ETag` từ response headers
3. Tạo request mới với header `If-None-Match: <etag_value>`
4. Gọi lại → nhận 304 Not Modified

### 5. GET - User Activities (private, no cache)

**Request:**
```
Method: GET
URL: http://localhost:5003/api/activities
```

**Response (200 OK):**
```json
{
  "success": true,
  "cached": false,
  "data": [],
  "timestamp": "2024-03-06T10:30:00.123456"
}
```

**Headers:**
- `Cache-Control: private, no-cache, must-revalidate`

**Giải thích:** Dữ liệu cá nhân không nên cache public

### 6. POST - Add Activity

**Request:**
```
Method: POST
URL: http://localhost:5003/api/activities
Headers: Content-Type: application/json
Body (raw JSON):
{
  "action": "Viewed product 123"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "action": "Viewed product 123",
    "timestamp": "2024-03-06T10:30:00.123456"
  }
}
```

## Kiểm tra Cache Headers trong Postman

### Cách xem response headers:
1. Gửi request
2. Chọn tab **Headers** trong response panel
3. Tìm các headers:
   - `Cache-Control`
   - `Expires`
   - `ETag`
   - `X-Generated-At`

### So sánh cached vs non-cached request:
1. Gọi `/api/products` → note `X-Generated-At` timestamp
2. Gọi lại ngay → timestamp giống = đã cache
3. Gọi `/api/products/no-cache` → timestamp luôn khác = không cache

## Cache Types

| Endpoint | Cache Type | Duration | Use Case |
|----------|-----------|----------|----------|
| `/api/products` | Public | 5 phút | Dữ liệu chung, ít thay đổi |
| `/api/products/:id` | Public | 2 phút | Chi tiết sản phẩm |
| `/api/products/no-cache` | No cache | - | Dữ liệu realtime |
| `/api/products/etag` | Public + ETag | 1 phút | Validation-based cache |
| `/api/activities` | Private | No cache | Dữ liệu cá nhân |

## Lợi ích của Cacheable

1. **Performance**: Giảm latency, response nhanh hơn
2. **Scalability**: Giảm tải server, xử lý nhiều users hơn
3. **Cost**: Tiết kiệm băng thông và tài nguyên server
4. **User Experience**: Trang load nhanh hơn
5. **Availability**: Có thể serve từ cache khi server down

## Cache Headers Cheat Sheet

### Cache-Control values:
- `public` - Cache được share giữa nhiều users
- `private` - Cache riêng từng user
- `no-cache` - Phải validate với server trước khi dùng
- `no-store` - Không cache
- `max-age=300` - Cache trong 300 giây
- `must-revalidate` - Cache hết hạn phải validate lại

### Best Practices:
- **Static data** (product catalog) → cache lâu (5-60 phút)
- **User-specific data** → private cache hoặc no-cache
- **Real-time data** → no-cache
- **Large responses** → dùng ETag để tiết kiệm băng thông

## Lưu ý

- Cache headers chỉ là gợi ý, browser/proxy có thể ignore
- Test cache behavior bằng cách so sánh timestamp
- Trong production, cân nhắc CDN cho static resources
- ETag giúp tiết kiệm băng thông cho large responses
