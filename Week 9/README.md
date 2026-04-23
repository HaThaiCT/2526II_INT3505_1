# Week 9: API Versioning & Deprecation Strategy

## 📚 Tổng Quan

Bài tập này mở rộng kiến thức từ Week 7 về OpenAPI, tập trung vào **chiến lược versioning và deprecation** cho REST API. Đây là một case study thực tế về việc nâng cấp Payment API từ v1 sang v2 một cách chuyên nghiệp.

---

## 🎯 Mục Tiêu Học Tập

Sau khi hoàn thành bài tập này, bạn sẽ hiểu:

1. ✅ **API Versioning Strategies**
   - URL versioning
   - Header versioning
   - Content negotiation
   - Pros & cons của mỗi approach

2. ✅ **Deprecation Best Practices**
   - HTTP headers (Deprecation, Sunset)
   - Communication strategy
   - Timeline planning
   - Developer support

3. ✅ **Breaking Changes Management**
   - Identifying breaking changes
   - Data migration strategy
   - Backward compatibility
   - Gradual rollout

4. ✅ **Real-world API Evolution**
   - Schema design improvements
   - Feature additions
   - Error handling enhancements
   - Maintaining stability

---

## 📁 Cấu Trúc Dự Án

```
Week 9/
├── app.py                      # Flask API với v1 (deprecated) và v2 (current)
├── openapi.yml                 # OpenAPI 3.0 spec cho cả v1 và v2
├── DEPRECATION_NOTICE.md       # Thông báo deprecation cho developers
├── UPGRADE_STRATEGY.md         # Chi tiết chiến lược nâng cấp
├── README.md                   # Tài liệu này
├── requirements.txt            # Dependencies
└── test_api.py                 # Test cases cho v1 và v2
```

---

## 🚀 Cài Đặt và Chạy

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Khởi động MongoDB

```bash
# Docker (recommended)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Hoặc MongoDB local
mongod
```

### 3. Chạy Flask API

```bash
python app.py
```

Server sẽ chạy tại: `http://localhost:5000`

### 4. Test API

```bash
# Run automated tests
python test_api.py

# Hoặc manual test với curl
curl http://localhost:5000/
```

---

## 📖 Key Concepts

### 1. API Versioning Strategy

#### URL Versioning (Đã implement)

```
✅ v1: /api/v1/payments  (DEPRECATED)
✅ v2: /api/v2/payments  (CURRENT)
```

**Ưu điểm:**
- Rõ ràng, dễ hiểu
- Dễ cache và route
- Industry standard (Stripe, Twitter, GitHub)

**Nhược điểm:**
- Duplicate code
- URL không stable lâu dài

#### Alternatives (Tham khảo)

**Header Versioning:**
```http
GET /api/payments HTTP/1.1
Accept-Version: v2
```

**Query Parameter:**
```http
GET /api/payments?version=2
```

**Content Negotiation:**
```http
GET /api/payments HTTP/1.1
Accept: application/vnd.example.v2+json
```

---

### 2. Deprecation Headers

#### Standard Headers (RFC 8594)

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: 2026-12-31
Link: </api/v2/docs>; rel="alternate"
X-API-Warn: This API version is deprecated...
```

**Ý nghĩa:**
- `Deprecation: true` - API đã deprecated
- `Sunset: 2026-12-31` - Ngày API sẽ bị tắt
- `Link` - Link tới version mới
- `X-API-Warn` - Warning message

---

### 3. Breaking Changes

#### v1 → v2 Breaking Changes

| Feature | v1 (Flat) | v2 (Nested) |
|---------|-----------|-------------|
| **Amount** | `amount: 100, currency: "USD"` | `amount: {value: 100, currency: "USD"}` |
| **Customer** | `customer_id: "123", customer_email: "..."` | `customer: {id: "123", email: "..."}` |
| **Payment Method** | `method: "card"` | `payment_method: {type: "card", details: {...}}` |

**Migration Pattern:**
```python
# v1 Request (old)
{
  "amount": 100.00,
  "currency": "USD",
  "customer_id": "CUST123",
  "method": "card"
}

# v2 Request (new)
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

---

### 4. Backward Compatibility Strategy

#### Internal Conversion Layer

```python
# v1 endpoint internally converts to v2
@app.route('/api/v1/payments', methods=['POST'])
def v1_create_payment():
    v1_data = request.get_json()
    
    # Convert v1 → v2 internally
    v2_data = convert_v1_to_v2(v1_data)
    
    # Store as v2
    result = db.insert_one(v2_data)
    
    # Convert back to v1 for response
    v1_response = convert_v2_to_v1(result)
    
    return jsonify(v1_response)
```

**Benefits:**
- ✅ No data migration needed
- ✅ Single source of truth (v2 schema)
- ✅ v1 still works during transition
- ✅ No downtime

---

## 🧪 Testing

### Run All Tests

```bash
python test_api.py
```

### Test Coverage

```
✓ v1 Basic operations (deprecated)
  ├─ Create payment
  ├─ List payments
  └─ Get payment by ID

✓ v2 Enhanced operations
  ├─ Create payment với nested structure
  ├─ List payments với filtering
  ├─ Get payment by ID
  ├─ Update payment
  ├─ Refund payment (NEW)
  └─ Get payment history (NEW)

✓ Deprecation headers
  ├─ Deprecation: true
  ├─ Sunset header
  └─ Warning messages

✓ Conversion compatibility
  ├─ v1 write → v2 read
  └─ v2 write → v1 read
```

### Manual Testing with cURL

#### v1 (Deprecated)

```bash
# Create payment v1
curl -X POST http://localhost:5000/api/v1/payments \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.00,
    "currency": "USD",
    "customer_id": "CUST123",
    "customer_email": "user@example.com",
    "method": "card"
  }'

# List payments v1
curl http://localhost:5000/api/v1/payments

# Get payment v1
curl http://localhost:5000/api/v1/payments/{payment_id}
```

#### v2 (Current)

```bash
# Create payment v2
curl -X POST http://localhost:5000/api/v2/payments \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: unique-key-123" \
  -d '{
    "amount": {
      "value": 100.00,
      "currency": "USD"
    },
    "customer": {
      "id": "CUST123",
      "email": "user@example.com",
      "name": "John Doe"
    },
    "payment_method": {
      "type": "card",
      "details": {
        "card_type": "visa"
      }
    }
  }'

# List payments v2
curl http://localhost:5000/api/v2/payments?status=pending&currency=USD

# Get payment v2
curl http://localhost:5000/api/v2/payments/{payment_id}

# Refund payment (NEW in v2)
curl -X POST http://localhost:5000/api/v2/payments/{payment_id}/refund \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.00,
    "reason": "Customer request"
  }'

# Get payment history (NEW in v2)
curl http://localhost:5000/api/v2/payments/{payment_id}/history
```

---

## 📊 API Endpoints

### General

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/migration-guide` | Migration guide v1→v2 |

### v1 (Deprecated) ⚠️

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/v1/docs` | v1 documentation | ⚠️ Deprecated |
| GET | `/api/v1/payments` | List payments | ⚠️ Deprecated |
| POST | `/api/v1/payments` | Create payment | ⚠️ Deprecated |
| GET | `/api/v1/payments/{id}` | Get payment | ⚠️ Deprecated |

### v2 (Current) ✅

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/v2/docs` | v2 documentation | ✅ Current |
| GET | `/api/v2/payments` | List payments (enhanced) | ✅ Current |
| POST | `/api/v2/payments` | Create payment (new structure) | ✅ Current |
| GET | `/api/v2/payments/{id}` | Get payment | ✅ Current |
| PUT | `/api/v2/payments/{id}` | Update payment | ✅ Current |
| POST | `/api/v2/payments/{id}/refund` | Refund payment | 🆕 New |
| GET | `/api/v2/payments/{id}/history` | Payment history | 🆕 New |

---

## 📝 Tài Liệu Chi Tiết

### 1. [DEPRECATION_NOTICE.md](DEPRECATION_NOTICE.md)

Thông báo chính thức cho developers về việc deprecate v1:
- Timeline chi tiết
- Breaking changes
- Migration instructions
- FAQ
- Contact information

### 2. [UPGRADE_STRATEGY.md](UPGRADE_STRATEGY.md)

Chiến lược kỹ thuật toàn diện:
- Versioning strategy comparison
- Architecture design
- Migration timeline
- Risk mitigation
- Rollback plan
- Success metrics
- Communication plan

### 3. [openapi.yml](openapi.yml)

OpenAPI 3.0 specification:
- v1 endpoints (marked deprecated)
- v2 endpoints (current)
- Schema definitions
- Examples
- Deprecation metadata

---

## 🎓 Best Practices Demonstrated

### 1. ✅ Clear Communication

```markdown
- 6+ months notice
- Multiple communication channels
- Regular reminders
- Clear documentation
- Support availability
```

### 2. ✅ Gradual Rollout

```timeline
Jun 2026 → Announcement
Jul 2026 → Beta testing
Aug 2026 → First check-in
Oct 2026 → 75% migration target
Dec 2026 → Sunset
```

### 3. ✅ Developer Experience

```
- Migration guide with examples
- Code samples in multiple languages
- Postman collection
- Testing tools
- Dedicated support
```

### 4. ✅ Technical Excellence

```python
- Backward compatibility via conversion
- No data migration needed
- Zero downtime
- Rollback capability
- Comprehensive testing
```

---

## 🔍 Real-world Examples

### Companies với Good Versioning

#### Stripe
```
https://api.stripe.com/v1/
- URL versioning
- Backward compatible changes
- Optional version pinning
```

#### GitHub
```
https://api.github.com/
- Header versioning: Accept: application/vnd.github.v3+json
- Sunset dates announced years in advance
```

#### Twitter
```
https://api.twitter.com/2/
- Major version in URL
- Clear migration paths
- Long deprecation periods
```

---

## 💡 Key Takeaways

### Do's ✅

1. **Plan Early**: Minimum 6 months notice
2. **Communicate Often**: Multiple channels, regular updates
3. **Provide Tools**: Make migration easy
4. **Support Generously**: Be available to help
5. **Test Thoroughly**: Avoid surprises
6. **Document Everything**: Clear, detailed guides
7. **Monitor Progress**: Track migration rate

### Don'ts ❌

1. **Don't Rush**: Short timelines cause problems
2. **Don't Break Silently**: Make changes obvious
3. **Don't Remove Docs**: Keep old docs until sunset
4. **Don't Ignore Feedback**: Listen to developers
5. **Don't Surprise Users**: Communicate changes early

---

## 📚 References & Further Reading

### Standards
- [RFC 8594 - Sunset HTTP Header](https://www.rfc-editor.org/rfc/rfc8594)
- [HTTP Status 410 Gone](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/410)

### Articles
- [REST API Versioning Strategies](https://www.baeldung.com/rest-versioning)
- [API Versioning Best Practices](https://swagger.io/blog/api-strategy/api-versioning/)
- [Evolving your APIs](https://stripe.com/blog/api-versioning)

### Real Examples
- [Stripe API Versioning](https://stripe.com/docs/api/versioning)
- [GitHub API Versions](https://docs.github.com/en/rest/overview/api-versions)
- [Twitter API Migration](https://developer.twitter.com/en/docs/twitter-api/migrate)

---

## ❓ Câu Hỏi Thảo Luận

1. **Khi nào nên tạo major version mới?**
   - Breaking changes
   - Fundamental redesign
   - Security requirements

2. **Làm sao balance giữa innovation và stability?**
   - Additive changes trong minor versions
   - Breaking changes chỉ trong major versions
   - Long support windows

3. **Có nên support nhiều versions cùng lúc?**
   - Pros: Flexibility cho developers
   - Cons: Maintenance burden
   - Balance: 2 versions max (current + deprecated)

4. **Làm gì khi developers không migrate?**
   - Multiple reminders
   - Grace period
   - Eventually enforce (410 Gone)

---

## 🤝 Contributing

Có ý tưởng cải thiện? Tạo issue hoặc pull request!

---

## 📞 Contact

- **Instructor**: [Your Name]
- **Email**: [Your Email]
- **Course**: Kiến Trúc Hướng Dịch Vụ (Service-Oriented Architecture)

---

**Version**: 1.0.0  
**Last Updated**: April 23, 2026  
**Status**: Active Assignment 🎯
