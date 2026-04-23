# 🚨 DEPRECATION NOTICE - Payment API v1

## Thông Báo Quan Trọng

**Payment API v1 sẽ bị tắt (sunset) vào ngày `31/12/2026`**

---

## 📅 Timeline

| Ngày | Sự kiện | Mô tả |
|------|---------|-------|
| **01/06/2026** | **Deprecation Announced** | v1 được đánh dấu deprecated, header cảnh báo được thêm vào |
| **31/08/2026** | **Reminder Sent** | Email nhắc nhở gửi đến tất cả developers |
| **30/11/2026** | **Final Warning** | Cảnh báo cuối cùng, 1 tháng trước khi tắt |
| **31/12/2026** | **🔴 SUNSET DATE** | v1 endpoints sẽ bị TẮT HOÀN TOÀN |

---

## ⚠️ Những Gì Bị Deprecated

### Deprecated Endpoints

| Endpoint | Status | Alternative |
|----------|--------|-------------|
| `GET /api/v1/payments` | ❌ Deprecated | `GET /api/v2/payments` |
| `POST /api/v1/payments` | ❌ Deprecated | `POST /api/v2/payments` |
| `GET /api/v1/payments/{id}` | ❌ Deprecated | `GET /api/v2/payments/{id}` |
| `PUT /api/v1/payments/{id}` | ❌ Deprecated | `PUT /api/v2/payments/{id}` |

### Deprecated Data Structure

**v1 Payment Object (Deprecated):**
```json
{
  "amount": 100.00,
  "currency": "USD",
  "customer_id": "CUST123",
  "customer_email": "user@example.com",
  "method": "card",
  "status": "pending"
}
```

---

## ✅ Giải Pháp Thay Thế

### Migrate to v2

**v2 Payment Object (Current):**
```json
{
  "amount": {
    "value": 100.00,
    "currency": "USD"
  },
  "customer": {
    "id": "CUST123",
    "email": "user@example.com",
    "name": "John Doe",
    "phone": "+1234567890"
  },
  "payment_method": {
    "type": "card",
    "details": {
      "card_type": "visa",
      "last4": "4242"
    },
    "provider": "stripe"
  },
  "metadata": {
    "order_id": "ORD-456",
    "source": "web"
  },
  "status": "pending"
}
```

---

## 🔔 Cách Nhận Biết Deprecation

### 1. HTTP Response Headers

Tất cả v1 endpoints sẽ trả về các headers sau:

```http
Deprecation: true
Sunset: 2026-12-31
Link: </api/v2/docs>; rel="alternate"
X-API-Warn: This API version is deprecated and will be removed on 2026-12-31. Please migrate to v2.
```

### 2. Response Body Warning

```json
{
  "success": true,
  "data": {...},
  "deprecation_warning": "This endpoint is deprecated. Please use /api/v2/payments. This version will be removed on 2026-12-31."
}
```

### 3. Email Notifications

Bạn sẽ nhận được email thông báo tại các mốc:
- ✉️ Thông báo đầu tiên: 01/06/2026
- ✉️ Nhắc nhở: Hàng tháng cho đến sunset date
- ✉️ Cảnh báo cuối: 01/12/2026

---

## 🚀 Hướng Dẫn Migration

### Bước 1: Đọc Migration Guide

Truy cập migration guide đầy đủ tại:
```
GET /migration-guide
```

### Bước 2: Cập Nhật Request Structure

**v1 Request (Old):**
```http
POST /api/v1/payments
Content-Type: application/json

{
  "amount": 100.00,
  "currency": "USD",
  "customer_id": "CUST123",
  "customer_email": "user@example.com",
  "method": "card"
}
```

**v2 Request (New):**
```http
POST /api/v2/payments
Content-Type: application/json
Idempotency-Key: unique-key-123

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
    "type": "card"
  }
}
```

### Bước 3: Test Với v2

1. Tạo môi trường test
2. Update code để call v2 endpoints
3. Verify response format
4. Test error handling

### Bước 4: Deploy Production

1. Deploy code mới với v2 integration
2. Monitor logs và errors
3. Verify không còn calls đến v1

---

## 📋 Breaking Changes

| Feature | v1 (Old) | v2 (New) | Impact |
|---------|----------|----------|--------|
| **Amount** | Flat fields | Nested object | 🔴 Breaking |
| **Customer** | Flat fields | Nested object | 🔴 Breaking |
| **Payment Method** | Simple string | Nested object | 🔴 Breaking |
| **Currencies** | USD, EUR, VND | +JPY, GBP | ✅ Additive |
| **Refunds** | ❌ Not supported | ✅ Supported | ✅ New feature |
| **History** | ❌ Not supported | ✅ Supported | ✅ New feature |
| **Idempotency** | ❌ Not supported | ✅ Supported | ✅ New feature |

---

## ❓ FAQ

### Q1: Tôi có thể tiếp tục dùng v1 sau sunset date không?

**A:** KHÔNG. Sau 31/12/2026, tất cả v1 endpoints sẽ trả về `410 Gone`.

### Q2: v1 và v2 có thể dùng song song không?

**A:** CÓ, cho đến sunset date. Nhưng nên migrate sớm nhất có thể.

### Q3: Data cũ có bị mất không?

**A:** KHÔNG. Data được lưu trong cùng database. v2 có thể đọc data từ v1.

### Q4: Tôi cần migrate tất cả cùng lúc không?

**A:** KHÔNG. Bạn có thể migrate từng endpoint một, nhưng phải hoàn thành trước sunset date.

### Q5: Có công cụ tự động migration không?

**A:** Chúng tôi cung cấp:
- Migration scripts samples
- Postman collection cho testing
- Code examples trong nhiều ngôn ngữ

### Q6: Nếu tôi gặp vấn đề trong quá trình migration?

**A:** Liên hệ support:
- 📧 Email: api-support@example.com
- 💬 Slack: #api-migration
- 📞 Phone: 1-800-API-HELP

---

## 🔗 Resources

- 📖 [Migration Guide](/migration-guide)
- 📘 [v2 API Documentation](/api/v2/docs)
- 📝 [Code Examples](https://github.com/example/payment-api-examples)
- 🧪 [Postman Collection](https://www.postman.com/example/payment-api-v2)
- 💡 [FAQ & Troubleshooting](https://docs.example.com/faq)

---

## 📞 Contact & Support

Nếu bạn cần hỗ trợ trong quá trình migration:

- **Email:** api-support@example.com
- **Slack Channel:** #payment-api-migration
- **Documentation:** https://docs.example.com/payment-api
- **Status Page:** https://status.example.com

---

## ⏱️ Countdown to Sunset

```
╔════════════════════════════════════════╗
║   v1 SUNSET DATE: December 31, 2026   ║
║                                        ║
║   ⏰ TIME REMAINING: 8 months          ║
║                                        ║
║   🚀 MIGRATE TO v2 NOW!                ║
╚════════════════════════════════════════╝
```

---

**Last Updated:** June 1, 2026  
**Version:** 1.0.0  
**Status:** 🔴 ACTIVE DEPRECATION
