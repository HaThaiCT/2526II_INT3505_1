# 🚀 QUICKSTART GUIDE - Week 9

Hướng dẫn nhanh để chạy và test Payment API với versioning strategy.

---

## ⚡ Setup Nhanh (5 phút)

### Bước 1: Clone/Chuyển vào folder Week 9

```bash
cd "Week 9"
```

### Bước 2: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 3: Khởi động MongoDB

**Option A: Docker (Khuyến nghị)**
```bash
docker run -d -p 27017:27017 --name mongodb-week9 mongo:latest
```

**Option B: MongoDB Local**
```bash
# Nếu đã cài MongoDB local
mongod
```

**Option C: MongoDB Atlas (Cloud - free tier)**
```bash
# Set environment variable
$env:MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/payment_api"
```

### Bước 4: Chạy API

```bash
python app.py
```

Output mong đợi:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Bước 5: Test API

**Terminal mới**, chạy:
```bash
python test_api.py
```

---

## 🧪 Test Thủ Công

### 1. Check API Info

```bash
curl http://localhost:5000/
```

Expected response:
```json
{
  "name": "Payment API",
  "versions": {
    "v1": {
      "status": "deprecated",
      "sunset_date": "2026-12-31"
    },
    "v2": {
      "status": "current"
    }
  }
}
```

### 2. Test v1 (Deprecated) - Với Deprecation Headers

```bash
# Tạo payment v1
curl -X POST http://localhost:5000/api/v1/payments \
  -H "Content-Type: application/json" \
  -d "{\"amount\": 100.00, \"currency\": \"USD\", \"customer_id\": \"CUST123\", \"method\": \"card\"}" \
  -i
```

Chú ý các **deprecation headers**:
- `Deprecation: true`
- `Sunset: 2026-12-31`
- `X-API-Warn: ...`

### 3. Test v2 (Current) - Với Structure Mới

```bash
# Tạo payment v2
curl -X POST http://localhost:5000/api/v2/payments \
  -H "Content-Type: application/json" \
  -d "{\"amount\": {\"value\": 200.00, \"currency\": \"USD\"}, \"customer\": {\"id\": \"CUST456\", \"email\": \"user@example.com\"}, \"payment_method\": {\"type\": \"card\"}}"
```

Response sẽ có cấu trúc nested:
```json
{
  "success": true,
  "data": {
    "_id": "...",
    "amount": {
      "value": 200.00,
      "currency": "USD"
    },
    "customer": {
      "id": "CUST456",
      "email": "user@example.com"
    },
    "payment_method": {
      "type": "card"
    }
  }
}
```

---

## 📖 Explore Features

### Feature 1: Migration Guide

```bash
curl http://localhost:5000/migration-guide | python -m json.tool
```

### Feature 2: v2 Refund (NEW)

```bash
# Lấy payment_id từ response trước
curl -X POST http://localhost:5000/api/v2/payments/{payment_id}/refund \
  -H "Content-Type: application/json" \
  -d "{\"amount\": 50.00, \"reason\": \"Customer request\"}"
```

### Feature 3: v2 History (NEW)

```bash
curl http://localhost:5000/api/v2/payments/{payment_id}/history
```

### Feature 4: Idempotency (NEW in v2)

```bash
# Gọi 2 lần với cùng Idempotency-Key → chỉ tạo 1 payment
curl -X POST http://localhost:5000/api/v2/payments \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: unique-key-123" \
  -d "{\"amount\": {\"value\": 300.00, \"currency\": \"EUR\"}, \"customer\": {\"id\": \"CUST789\"}, \"payment_method\": {\"type\": \"bank_transfer\"}}"
```

---

## 🎯 Key Learning Points

### 1. Compare Structures

**v1 (Flat Structure):**
```json
{
  "amount": 100.00,
  "currency": "USD",
  "customer_id": "CUST123",
  "method": "card"
}
```

**v2 (Nested Structure):**
```json
{
  "amount": {
    "value": 100.00,
    "currency": "USD"
  },
  "customer": {
    "id": "CUST123",
    "email": "user@example.com"
  },
  "payment_method": {
    "type": "card",
    "details": {}
  }
}
```

### 2. Deprecation Strategy

```
┌─────────────────────────────────────┐
│  v1 (Wrapper Layer)                 │
│  ├─ Accepts old format              │
│  ├─ Converts to v2 internally       │
│  ├─ Returns deprecation headers     │
│  └─ Shows migration warnings        │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  v2 (Native Implementation)         │
│  ├─ New nested structure            │
│  ├─ Enhanced features               │
│  └─ Better extensibility            │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  Database (Single Schema - v2)      │
│  ├─ All data stored as v2          │
│  └─ No migration needed             │
└─────────────────────────────────────┘
```

### 3. Timeline Understanding

```
JUN 2026 ─┬─ Deprecation announced
          │  • Headers added
          │  • Docs published
          │
AUG 2026 ─┤  First checkpoint
          │
OCT 2026 ─┤  75% migration target
          │
DEC 2026 ─┴─ SUNSET DATE
             • v1 returns 410 Gone
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| [README.md](README.md) | Tổng quan dự án |
| [DEPRECATION_NOTICE.md](DEPRECATION_NOTICE.md) | Thông báo chính thức cho developers |
| [UPGRADE_STRATEGY.md](UPGRADE_STRATEGY.md) | Chiến lược kỹ thuật chi tiết |
| [openapi.yml](openapi.yml) | OpenAPI specification |
| [app.py](app.py) | Source code API |
| [test_api.py](test_api.py) | Test suite |

---

## 🐛 Common Issues

### Issue 1: Cannot connect to MongoDB

```bash
# Check if MongoDB is running
docker ps | grep mongo

# Restart MongoDB
docker restart mongodb-week9

# Or start new
docker run -d -p 27017:27017 --name mongodb-week9 mongo:latest
```

### Issue 2: Port 5000 already in use

```python
# Edit app.py, change port
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change to 5001
```

### Issue 3: Module not found

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 💡 Learning Tasks

### Task 1: Explore Deprecation Headers
- [ ] Create v1 payment và check response headers
- [ ] So sánh v1 vs v2 headers
- [ ] Đọc hiểu Sunset header

### Task 2: Test Conversions
- [ ] Create payment với v1, read với v2
- [ ] Create payment với v2, read với v1
- [ ] Verify data integrity

### Task 3: Try New v2 Features
- [ ] Refund a payment
- [ ] Get payment history
- [ ] Test idempotency

### Task 4: Understand Breaking Changes
- [ ] List all breaking changes từ migration guide
- [ ] Explain why each change is breaking
- [ ] Propose migration strategy

---

## 🎓 Discussion Questions

1. **Tại sao chọn URL versioning thay vì header versioning?**
   - Pros and cons?
   - Khi nào nên dùng approach nào?

2. **6 months notice có đủ không?**
   - Phụ thuộc vào factors nào?
   - Companies lớn thường cho bao lâu?

3. **Làm sao enforce developers migrate?**
   - Carrot vs stick approach?
   - Rate limiting? Hard cutoff?

4. **v2 có những improvements gì so với v1?**
   - Structure improvements
   - New features
   - Extensibility

---

## 🔗 Next Steps

1. ✅ Chạy và test API
2. 📖 Đọc DEPRECATION_NOTICE.md
3. 📖 Đọc UPGRADE_STRATEGY.md
4. 🧪 Chạy test_api.py
5. 📝 Viết reflection về versioning strategy
6. 💬 Thảo luận với team về best practices

---

## ✨ Bonus Challenges

### Challenge 1: Add API Key Authentication
```python
# Implement API key auth for both v1 and v2
```

### Challenge 2: Add Rate Limiting
```python
# v1: Lower rate limit (to encourage migration)
# v2: Higher rate limit
```

### Challenge 3: Monitoring Dashboard
```python
# Track v1 vs v2 usage
# Visualize migration progress
```

### Challenge 4: Auto-Migration Script
```python
# Script to convert v1 calls to v2
# For helping developers migrate
```

---

**Happy Learning! 🎉**

Questions? Check [README.md](README.md) or contact instructor.
