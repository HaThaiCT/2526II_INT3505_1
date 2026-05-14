# Library API System - Logging, Monitoring & Rate Limiting

Một API library system hoàn chỉnh sử dụng Flask với các tính năng:
- **Logging**: Structured logging với JSON format
- **Monitoring**: Prometheus metrics để theo dõi performance
- **Rate Limiting**: Giới hạn tần suất requests

## 🚀 Quick Start

### 1. Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### 2. Chạy Server

```bash
python app.py
```

Server sẽ chạy tại `http://localhost:5000`

### 3. Kiểm tra Health

```bash
curl http://localhost:5000/health
```

## 📊 Logging System

### Đặc điểm

- **Structured JSON Logging**: Tất cả logs được format thành JSON để dễ parse
- **Dual Output**: Logs ghi vào file `library_api.log` và console
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Context**: Mỗi log chứa timestamp, module, function, line number

### Log Format

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "level": "INFO",
  "logger": "library_api",
  "message": "Request completed",
  "module": "app",
  "function": "track_metrics",
  "line": 156,
  "method": "GET",
  "endpoint": "get_books",
  "status": 200,
  "duration": 0.045,
  "ip": "127.0.0.1"
}
```

### Kiểm tra Logs

Xem file logs:
```bash
type library_api.log  # Windows
# hoặc
cat library_api.log   # Linux/Mac
```

## 📈 Prometheus Monitoring

### Metrics được theo dõi

1. **library_api_requests_total**: Tổng số requests
   - Labels: method, endpoint, status
   
2. **library_api_request_duration_seconds**: Thời gian xử lý request
   - Labels: method, endpoint, status
   - Buckets: 0.1s, 0.5s, 1s, 2s, 5s
   
3. **library_api_active_requests**: Số requests đang xử lý
   - Labels: endpoint
   
4. **library_api_books_count**: Tổng số sách trong hệ thống
   
5. **library_api_rate_limit_exceeded_total**: Số lần vượt giới hạn
   - Labels: endpoint

### Xem Metrics

Truy cập endpoint metrics:
```bash
curl http://localhost:5000/metrics
```

### Kết nối với Prometheus

Thêm vào `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'library_api'
    static_configs:
      - targets: ['localhost:5000']
```

## ⏱️ Rate Limiting

### Cấu hình

Mỗi endpoint có giới hạn riêng:

| Endpoint | Method | Limit | Mục đích |
|----------|--------|-------|---------|
| `/health` | GET | None | Health check không giới hạn |
| `/books` | GET | 30/min | Lấy danh sách sách |
| `/books/<id>` | GET | 60/min | Lấy chi tiết sách |
| `/books` | POST | 10/min | Tạo sách mới |
| `/books/<id>/borrow` | POST | 20/min | Mượn sách |
| `/books/<id>/return` | POST | 20/min | Trả sách |
| `/books/<id>` | DELETE | 5/min | Xóa sách |
| `/stats` | GET | 30/min | Lấy thống kê |

### Rate Limit Exceeded Response

Khi vượt quá giới hạn, server trả về:
```json
HTTP/1.1 429 Too Many Requests
{
  "error": "Rate limit exceeded"
}
```

## 🔧 API Endpoints

### Health Check
```bash
curl http://localhost:5000/health
```

### Get All Books
```bash
curl http://localhost:5000/books
```

### Get Book by ID
```bash
curl http://localhost:5000/books/1
```

### Create New Book
```bash
curl -X POST http://localhost:5000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Programming",
    "author": "Mark Lutz",
    "available": 3
  }'
```

### Borrow a Book
```bash
curl -X POST http://localhost:5000/books/1/borrow
```

### Return a Book
```bash
curl -X POST http://localhost:5000/books/1/return
```

### Delete a Book
```bash
curl -X DELETE http://localhost:5000/books/1
```

### Get Statistics
```bash
curl http://localhost:5000/stats
```

### Get Prometheus Metrics
```bash
curl http://localhost:5000/metrics
```

## 📝 Test Script

Tạo file `test_api.py`:

```python
import requests
import time

BASE_URL = "http://localhost:5000"

def test_api():
    # Test health check
    print("1. Health Check")
    resp = requests.get(f"{BASE_URL}/health")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}\n")
    
    # Test get all books
    print("2. Get All Books")
    resp = requests.get(f"{BASE_URL}/books")
    print(f"Status: {resp.status_code}")
    print(f"Books: {len(resp.json()['books'])} books\n")
    
    # Test borrow book
    print("3. Borrow Book")
    resp = requests.post(f"{BASE_URL}/books/1/borrow")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}\n")
    
    # Test create book
    print("4. Create New Book")
    resp = requests.post(f"{BASE_URL}/books", json={
        "title": "AI Fundamentals",
        "author": "John Smith",
        "available": 2
    })
    print(f"Status: {resp.status_code}")
    print(f"New Book: {resp.json()['book']}\n")
    
    # Test rate limiting
    print("5. Test Rate Limiting (rapid requests)")
    for i in range(5):
        resp = requests.get(f"{BASE_URL}/books")
        print(f"Request {i+1}: Status {resp.status_code}")
        if resp.status_code == 429:
            print("Rate limit reached!")
            break
        time.sleep(0.1)

if __name__ == "__main__":
    test_api()
```

Chạy test:
```bash
python test_api.py
```

## 📊 Monitoring Dashboard

Để tạo dashboard Grafana:

1. Cài đặt Prometheus
2. Cài đặt Grafana
3. Kết nối Grafana với Prometheus
4. Import dashboard hoặc tạo queries:

**Query examples:**
```
# Request rate per second
rate(library_api_requests_total[1m])

# Average request duration
avg(library_api_request_duration_seconds)

# 95th percentile latency
histogram_quantile(0.95, library_api_request_duration_seconds_bucket)

# Active requests
library_api_active_requests

# Rate limit events
rate(library_api_rate_limit_exceeded_total[1m])
```

## 🔍 Troubleshooting

### 1. Logs không xuất hiện

Kiểm tra quyền ghi file trong thư mục hiện tại.

### 2. Rate limiting không hoạt động

- Xác nhận endpoint được decorator `@limiter.limit()`
- Kiểm tra header `X-Forwarded-For` nếu chạy behind proxy

### 3. Prometheus metrics không xuất hiện

Truy cập `/metrics` endpoint để xác nhận metrics được generate.

## 🎯 Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────┐
│      Flask Application          │
├─────────────────────────────────┤
│ • Routing                       │
│ • Rate Limiter (Flask-Limiter) │
│ • Metrics (Prometheus-client)   │
│ • Logging (JSON structured)     │
└──────┬──────────────────────────┘
       │
       ├─→ File: library_api.log
       ├─→ Console: STDOUT
       └─→ Metrics: /metrics endpoint
```

## 📦 Dependencies

- **Flask**: Web framework
- **Flask-Limiter**: Rate limiting
- **prometheus-client**: Metrics collection
- **python-json-logger**: JSON logging

## 🚀 Production Considerations

1. **Logging**: Sử dụng centralized logging (ELK stack, Datadog, etc.)
2. **Metrics**: Deploy Prometheus + Grafana
3. **Rate Limiting**: Sử dụng Redis backend thay vì in-memory
4. **Performance**: Cân nhân viên xử lý concurrent requests
5. **Security**: Thêm authentication/authorization layer

## 📚 References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-Limiter](https://flask-limiter.readthedocs.io/)
- [Prometheus Client](https://github.com/prometheus/client_python)
- [Structured Logging](https://www.kartar.net/2015/12/structured-logging/)
