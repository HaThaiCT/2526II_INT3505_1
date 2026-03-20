# PHÂN TÍCH 3 API PHỔ BIẾN

## Mục lục
1. [GitHub API](#1-github-api)
2. [OpenWeather API](#2-openweather-api)
3. [Stripe API](#3-stripe-api)

---

## 1. GITHUB API

### 1.1. Tổng quan
- **Nhà cung cấp**: GitHub, Inc. (Microsoft)
- **URL chính**: `https://api.github.com`
- **Phiên bản hiện tại**: REST API v3, GraphQL API v4
- **Mục đích**: Quản lý repository, issues, pull requests, users, organizations

### 1.2. Đặc điểm chính

#### Authentication
- Personal Access Token (PAT)
- OAuth 2.0
- GitHub Apps
- API key không yêu cầu đối với các request giới hạn (60 requests/hour)

#### Rate Limiting
- **Không xác thực**: 60 requests/giờ
- **Có xác thực**: 5,000 requests/giờ
- **GraphQL API**: 5,000 points/giờ

### 1.3. Các endpoint quan trọng

#### a) Repositories
```http
GET /repos/{owner}/{repo}
```
**Mô tả**: Lấy thông tin về repository

**Response mẫu**:
```json
{
  "id": 123456789,
  "name": "demo-repo",
  "full_name": "user/demo-repo",
  "private": false,
  "description": "Demo repository",
  "stargazers_count": 100,
  "forks_count": 25,
  "language": "JavaScript"
}
```

#### b) Issues
```http
GET /repos/{owner}/{repo}/issues
POST /repos/{owner}/{repo}/issues
```
**Mô tả**: Quản lý issues trong repository

**Request body (POST)**:
```json
{
  "title": "Bug found",
  "body": "Description of the bug",
  "labels": ["bug", "urgent"]
}
```

#### c) Users
```http
GET /users/{username}
GET /user (authenticated user)
```
**Mô tả**: Lấy thông tin người dùng

### 1.4. Ưu điểm
+ Documentation chi tiết và rõ ràng  
+ Hỗ trợ cả REST và GraphQL  
+ Rate limiting hợp lý  
+ Webhook cho real-time updates  
+ SDK cho nhiều ngôn ngữ (Octokit)  

### 1.5. Nhược điểm
+ Rate limiting nghiêm ngặt với tài khoản miễn phí  
+  Một số tính năng chỉ có trên GitHub Apps  
+ Complexity cao với GraphQL API  

### 1.6. Use cases
- Tự động hóa CI/CD workflows
- Quản lý dự án và issue tracking
- Code review automation
- Analytics và reporting
- Integration với các công cụ DevOps

### 1.7. Ví dụ sử dụng

```javascript
const axios = require('axios');

async function getRepository(owner, repo) {
  try {
    const response = await axios.get(
      `https://api.github.com/repos/${owner}/${repo}`,
      {
        headers: {
          'Authorization': 'token YOUR_TOKEN',
          'Accept': 'application/vnd.github.v3+json'
        }
      }
    );
    console.log(response.data);
  } catch (error) {
    console.error(error.response.data);
  }
}

getRepository('octocat', 'Hello-World');
```

---

## 2. OPENWEATHER API

### 2.1. Tổng quan
- **Nhà cung cấp**: OpenWeather Ltd.
- **URL chính**: `https://api.openweathermap.org/data/2.5`
- **Phiên bản**: 2.5 (Current Weather), 3.0 (One Call API)
- **Mục đích**: Cung cấp dữ liệu thời tiết, dự báo, lịch sử

### 2.2. Đặc điểm chính

#### Authentication
- API Key (appid parameter)
- Free tier: 60 calls/phút, 1,000,000 calls/tháng

#### Pricing
- **Free**: 60 calls/phút
- **Startup**: $40/tháng - 100,000 calls/ngày
- **Developer**: $125/tháng - 500,000 calls/ngày
- **Professional**: Custom pricing

### 2.3. Các endpoint quan trọng

#### a) Current Weather
```http
GET /weather?q={city}&appid={API_KEY}
GET /weather?lat={lat}&lon={lon}&appid={API_KEY}
```
**Mô tả**: Lấy thời tiết hiện tại theo tên thành phố hoặc tọa độ

**Response mẫu**:
```json
{
  "coord": {"lon": 106.6667, "lat": 10.75},
  "weather": [
    {
      "id": 801,
      "main": "Clouds",
      "description": "few clouds"
    }
  ],
  "main": {
    "temp": 302.15,
    "feels_like": 305.2,
    "temp_min": 301.15,
    "temp_max": 303.15,
    "pressure": 1012,
    "humidity": 70
  },
  "wind": {"speed": 3.5, "deg": 180},
  "name": "Ho Chi Minh City"
}
```

#### b) 5-Day Forecast
```http
GET /forecast?q={city}&appid={API_KEY}
```
**Mô tả**: Dự báo thời tiết 5 ngày, cập nhật 3 giờ/lần

#### c) One Call API (3.0)
```http
GET /onecall?lat={lat}&lon={lon}&exclude={part}&appid={API_KEY}
```
**Mô tả**: Dữ liệu thời tiết đầy đủ (hiện tại, phút, giờ, ngày, alerts)

**Parameters**:
- `exclude`: current, minutely, hourly, daily, alerts
- `units`: metric, imperial, standard

### 2.4. Ưu điểm
+ Dữ liệu toàn cầu, cập nhật liên tục  
+ Free tier hào phóng (1M calls/tháng)  
+ Nhiều loại dữ liệu (hiện tại, dự báo, lịch sử)  
+ Hỗ trợ nhiều đơn vị (metric, imperial)  
+ API đơn giản, dễ sử dụng  
+ Historical data available  

### 2.5. Nhược điểm
+ Độ chính xác có thể thay đổi theo vị trí  
+ Một số tính năng cao cấp cần trả phí  
+ Rate limiting khá chặt ở free tier (60/phút)  
+ Historical data chỉ có ở gói trả phí  

### 2.6. Use cases
- Ứng dụng thời tiết mobile/web
- Nông nghiệp thông minh (smart farming)
- Logistics và vận tải
- Du lịch và hospitality
- Event planning
- IoT và smart home

### 2.7. Ví dụ sử dụng

```javascript
const API_KEY = 'your_api_key';
const city = 'Hanoi';

async function getCurrentWeather(city) {
  const url = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${API_KEY}&units=metric`;
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    
    console.log(`Thành phố: ${data.name}`);
    console.log(`Nhiệt độ: ${data.main.temp}°C`);
    console.log(`Thời tiết: ${data.weather[0].description}`);
    console.log(`Độ ẩm: ${data.main.humidity}%`);
  } catch (error) {
    console.error('Error:', error);
  }
}

getCurrentWeather(city);
```

---

## 3. STRIPE API

### 3.1. Tổng quan
- **Nhà cung cấp**: Stripe, Inc.
- **URL chính**: `https://api.stripe.com/v1`
- **Phiên bản hiện tại**: v1 (với versioning theo ngày)
- **Mục đích**: Xử lý thanh toán online, subscriptions, billing

### 3.2. Đặc điểm chính

#### Authentication
- API Keys (Secret key, Publishable key)
- **Test mode**: sk_test_*, pk_test_*
- **Live mode**: sk_live_*, pk_live_*
- Bearer token authentication

#### Security
- PCI DSS compliant
- 3D Secure support
- Fraud detection (Radar)
- Webhook signatures

#### Pricing
- **2.9% + 200 VND** per successful card charge (Vietnam)
- **3.4% + 200 VND** for international cards
- No setup fees, monthly fees

### 3.3. Các endpoint quan trọng

#### a) Payment Intents
```http
POST /v1/payment_intents
GET /v1/payment_intents/{id}
POST /v1/payment_intents/{id}/confirm
```
**Mô tả**: Tạo và quản lý payment intent (phương thức thanh toán hiện đại)

**Request body (POST)**:
```json
{
  "amount": 2000,
  "currency": "vnd",
  "payment_method_types": ["card"],
  "description": "Payment for order #1234"
}
```

**Response mẫu**:
```json
{
  "id": "pi_1234567890",
  "object": "payment_intent",
  "amount": 2000,
  "currency": "vnd",
  "status": "requires_payment_method",
  "client_secret": "pi_1234_secret_abcdef",
  "created": 1677654321
}
```

#### b) Customers
```http
POST /v1/customers
GET /v1/customers/{id}
PUT /v1/customers/{id}
DELETE /v1/customers/{id}
```
**Mô tả**: Quản lý thông tin khách hàng

**Create customer**:
```json
{
  "email": "customer@example.com",
  "name": "Nguyen Van A",
  "description": "VIP Customer",
  "metadata": {
    "user_id": "12345"
  }
}
```

#### c) Subscriptions
```http
POST /v1/subscriptions
GET /v1/subscriptions/{id}
PUT /v1/subscriptions/{id}
DELETE /v1/subscriptions/{id}
```
**Mô tả**: Quản lý đăng ký định kỳ

#### d) Charges (Legacy)
```http
POST /v1/charges
GET /v1/charges/{id}
```
**Mô tả**: Tạo charge trực tiếp (nên dùng Payment Intents thay thế)

### 3.4. Ưu điểm
+ Documentation xuất sắc với examples  
+ Security và compliance cao (PCI DSS)  
+ SDK cho hầu hết các ngôn ngữ  
+ Test mode hoàn chỉnh  
+ Stripe CLI cho development  
+ Webhooks mạnh mẽ  
+ Dashboard trực quan  
+ Hỗ trợ nhiều phương thức thanh toán  
+ Fraud detection tích hợp (Radar)  

### 3.5. Nhược điểm
+ Phí giao dịch cao hơn một số đối thủ  
+ Không hỗ trợ tất cả quốc gia  
+ Complexity cao cho use cases đơn giản  
+ Một số tính năng chỉ có ở thị trường nhất định  

### 3.6. Use cases
- E-commerce platforms
- SaaS subscription billing
- Marketplace payments
- Crowdfunding platforms
- Mobile app payments
- Recurring billing
- Multi-currency transactions

### 3.7. Ví dụ sử dụng

```javascript
const stripe = require('stripe')('sk_test_your_key');

async function createPayment() {
  try {
    const paymentIntent = await stripe.paymentIntents.create({
      amount: 100000, 
      currency: 'vnd',
      payment_method_types: ['card'],
      description: 'Thanh toán đơn hàng #12345',
    });
    
    console.log('Payment Intent created:', paymentIntent.id);
    return paymentIntent.client_secret;
  } catch (error) {
    console.error('Error:', error);
  }
}

async function createCustomer() {
  const customer = await stripe.customers.create({
    email: 'customer@example.com',
    name: 'Trần Thị B',
    metadata: {
      user_id: '54321',
      source: 'web'
    }
  });
  
  return customer.id;
}

async function createSubscription(customerId, priceId) {
  const subscription = await stripe.subscriptions.create({
    customer: customerId,
    items: [{ price: priceId }],
    trial_period_days: 14,
  });
  
  return subscription;
}
```

### 3.8. Webhooks

**Endpoint setup**:
```javascript
const express = require('express');
const app = express();

app.post('/webhook', express.raw({type: 'application/json'}), (req, res) => {
  const sig = req.headers['stripe-signature'];
  const endpointSecret = 'whsec_your_secret';
  
  let event;
  
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
  } catch (err) {
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }
  
  // Handle the event
  switch (event.type) {
    case 'payment_intent.succeeded':
      const paymentIntent = event.data.object;
      console.log('PaymentIntent was successful!');
      break;
    case 'payment_intent.payment_failed':
      console.log('Payment failed!');
      break;
    default:
      console.log(`Unhandled event type ${event.type}`);
  }
  
  res.json({received: true});
});
```

---

## Tài nguyên tham khảo

- **GitHub API**: https://docs.github.com/en/rest
- **OpenWeather API**: https://openweathermap.org/api
- **Stripe API**: https://stripe.com/docs/api

