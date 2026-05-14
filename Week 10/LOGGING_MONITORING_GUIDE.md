# Logging & Monitoring Implementation Guide

## 📋 Table of Contents

1. [Logging Setup](#logging-setup)
2. [Prometheus Monitoring](#prometheus-monitoring)
3. [Rate Limiting](#rate-limiting)
4. [Best Practices](#best-practices)
5. [Troubleshooting](#troubleshooting)

---

## 🎯 Logging Setup

### 1. JSON Structured Logging

**Lợi ích:**
- Dễ parse bằng log aggregation tools (ELK, Splunk, etc.)
- Chứa context thông tin đầy đủ
- Tương thích với centralized logging

**Implementation:**
```python
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        return json.dumps(log_data, ensure_ascii=False)
```

### 2. Logging Levels

| Level | Usage | Example |
|-------|-------|---------|
| DEBUG | Chi tiết cho development | Variable values, function entry |
| INFO | General information | Request completion, resource created |
| WARNING | Something unexpected | Book not found, rate limit exceeded |
| ERROR | Error but app continues | Failed API call, validation error |
| CRITICAL | Serious error | Database connection failed |

### 3. Structured Logging Pattern

```python
logger.info("User action", extra={
    'user_id': user_id,
    'action': 'create_book',
    'book_title': title,
    'timestamp': datetime.utcnow().isoformat()
})
```

### 4. Log Correlation

```python
# Add unique ID to track related logs
request_id = str(uuid.uuid4())
logger.info("Request started", extra={'request_id': request_id})
# ... process ...
logger.info("Request completed", extra={'request_id': request_id})
```

---

## 📊 Prometheus Monitoring

### 1. Metric Types

#### Counter (Tăng không giảm)
```python
requests_total = Counter(
    'library_api_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Usage
requests_total.labels(method='GET', endpoint='/books', status=200).inc()
```

**Queries:**
```
rate(library_api_requests_total[1m])  # Requests per second
```

#### Histogram (Distribution)
```python
request_duration = Histogram(
    'library_api_request_duration_seconds',
    'HTTP request duration',
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

# Usage
request_duration.labels(...).observe(0.234)
```

**Queries:**
```
histogram_quantile(0.95, request_duration_bucket)  # 95th percentile
avg(rate(request_duration_sum[5m]) / rate(request_duration_count[5m]))  # Average
```

#### Gauge (Can go up/down)
```python
active_requests = Gauge(
    'library_api_active_requests',
    'Active requests',
    ['endpoint']
)

# Usage
active_requests.labels(endpoint='/books').inc()
active_requests.labels(endpoint='/books').dec()
```

**Queries:**
```
library_api_active_requests  # Current value
```

### 2. Key Prometheus Queries

```promql
# Request rate (requests/sec)
rate(library_api_requests_total[1m])

# Success rate
sum(rate(library_api_requests_total{status=~"2.."}[1m])) 
/ 
sum(rate(library_api_requests_total[1m]))

# Error rate
sum(rate(library_api_requests_total{status=~"5.."}[1m]))

# Response time percentiles
histogram_quantile(0.50, library_api_request_duration_seconds_bucket)  # Median
histogram_quantile(0.95, library_api_request_duration_seconds_bucket)  # 95th
histogram_quantile(0.99, library_api_request_duration_seconds_bucket)  # 99th

# Requests by endpoint
sum(rate(library_api_requests_total[1m])) by (endpoint)

# Failed requests
sum(rate(library_api_requests_total{status=~"4..5.."}[1m])) by (endpoint)
```

### 3. Setting up Prometheus

**Download:** https://prometheus.io/download/

**Windows Command:**
```bash
# Extract prometheus-X.Y.Z.windows-amd64.zip
cd prometheus-X.Y.Z.windows-amd64

# Run with custom config
.\prometheus.exe --config.file=prometheus.yml

# Access at http://localhost:9090
```

### 4. Grafana Dashboard

**Install Grafana:** https://grafana.com/grafana/download

**Example Dashboard:**
```json
{
  "dashboard": {
    "title": "Library API",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {"expr": "rate(library_api_requests_total[1m])"}
        ]
      },
      {
        "title": "Response Time (95th)",
        "targets": [
          {"expr": "histogram_quantile(0.95, library_api_request_duration_seconds_bucket)"}
        ]
      },
      {
        "title": "Active Requests",
        "targets": [
          {"expr": "library_api_active_requests"}
        ]
      }
    ]
  }
}
```

---

## ⏱️ Rate Limiting

### 1. How Flask-Limiter Works

```python
from flask_limiter import Limiter

limiter = Limiter(
    app=app,
    key_func=get_remote_address,  # Use IP address as key
    storage_uri="memory://"         # In-memory storage
)
```

### 2. Limit Patterns

```
"30 per minute"      # 30 requests per minute
"10 per hour"        # 10 requests per hour
"200 per day"        # 200 requests per day
"100 per 1 hour"     # Explicit duration
```

### 3. Different Limits for Different Endpoints

```python
@app.route('/expensive-operation', methods=['POST'])
@limiter.limit("5 per minute")
def expensive():
    return process_expensive_operation()

@app.route('/cheap-operation', methods=['GET'])
@limiter.limit("100 per minute")
def cheap():
    return get_data()
```

### 4. Redis Backend (Production)

```python
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"  # Production backend
)
```

**Setup Redis:**
```bash
# Windows: Use WSL or Docker
docker run -d -p 6379:6379 redis

# Or download from: https://github.com/microsoftarchive/redis
redis-server.exe
```

### 5. Rate Limit Headers

Prometheus Metrics return:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 15
X-RateLimit-Reset: 1705324800
```

---

## ✅ Best Practices

### 1. Logging Best Practices

✓ **DO:**
- Log at appropriate levels
- Include context information
- Use structured logging
- Sanitize sensitive data
- Log errors with full stack trace

✗ **DON'T:**
- Log passwords or tokens
- Log in loops
- Use generic messages
- Ignore exception information
- Mix different log formats

```python
# Good
logger.warning("Failed login attempt", extra={
    'user_id': user_id,
    'ip': request.remote_addr
})

# Bad
logger.warning("Error")
logger.info(f"User password: {password}")  # Never!
```

### 2. Monitoring Best Practices

✓ **DO:**
- Monitor business metrics (request rate, success rate)
- Track performance metrics (latency, errors)
- Set up alerts for anomalies
- Keep metrics retention reasonable
- Use dashboards for visualization

✗ **DON'T:**
- Monitor everything
- Ignore performance impact
- Keep excessive data retention
- Alert on every metric change
- Forget to test alerts

```python
# Good - Track meaningful metrics
requests_total = Counter('requests_total', 'Total requests', ['endpoint', 'status'])
response_time = Histogram('response_time_seconds', 'Response time', buckets=[...])

# Bad - Too granular
every_request_detail = Gauge('detail_' + str(uuid.uuid4()), '...')
```

### 3. Rate Limiting Best Practices

✓ **DO:**
- Set reasonable limits per endpoint
- Consider user types (public, registered)
- Use persistent storage in production
- Return informative rate limit responses
- Monitor rate limit violations

✗ **DON'T:**
- Set limits too tight
- Use in-memory storage in production
- Ignore rate limit exceeded events
- Rate limit health check endpoints
- Implement poorly without fallback

```python
# Good - Different limits by endpoint
@limiter.limit("100 per hour")
def expensive_operation():
    ...

# Good - No limit on health check
@app.route('/health')
def health():
    ...

# Bad - Same limit for all
@app.route('/anything')
@limiter.limit("10 per minute")
def everything():
    ...
```

---

## 🔧 Troubleshooting

### Problem 1: Logs Not Appearing

**Symptoms:** No log file created

**Solutions:**
```bash
# Check directory permissions
cd c:\Users\admin\OneDrive\Desktop\Kiến trúc hướng dịch vụ\Week 10
dir  # Should show permissions

# Check Flask app path
# Make sure app.py is in correct directory
```

### Problem 2: Rate Limiting Not Working

**Symptoms:** All requests succeed despite limit

**Solutions:**
```python
# Verify decorator is present
@limiter.limit("30 per minute")  # Must have this
def my_endpoint():
    ...

# Check if app has limiter initialized
if not hasattr(app, 'limiter'):
    limiter.init_app(app)

# For behind proxy, add:
app.config['BEHIND_PROXY'] = True
limiter = Limiter(
    app=app,
    key_func=lambda: request.headers.get('X-Forwarded-For'),
    storage_uri="memory://"
)
```

### Problem 3: Prometheus Metrics Empty

**Symptoms:** /metrics endpoint returns no metrics

**Solutions:**
```python
# Verify REGISTRY has metrics
from prometheus_client import REGISTRY
print(list(REGISTRY.collect()))

# Make sure metrics are created before use
request_total = Counter(...)  # Create at module level

# Verify endpoint returns metrics
response = requests.get('http://localhost:5000/metrics')
print(response.text[:200])
```

### Problem 4: Memory Issues

**Symptoms:** Memory usage increases over time

**Solutions:**
```python
# Add metrics cleanup
# For in-memory limiter with many clients
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=["200 per day"]  # Set reasonable defaults
)

# For Prometheus, set reasonable retention
# In prometheus.yml:
# storage:
#   retention:
#     time: 30d
```

---

## 📈 Performance Tips

### 1. Optimize Logging

```python
# Don't log in tight loops
for item in large_list:
    logger.debug(f"Processing {item}")  # Bad

# Instead, log summary
logger.info(f"Processed {len(large_list)} items")  # Good
```

### 2. Optimize Metrics

```python
# Limit cardinality (unique label combinations)
# Good - Limited labels
status_code = Counter('requests', 'Count', ['endpoint', 'status'])

# Bad - Too many unique values
request_id = Counter('requests', 'Count', ['request_id'])  # Every request is unique!
```

### 3. Optimize Rate Limiting

```python
# Production: Use Redis instead of memory
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)

# Add exemption for trusted endpoints
@app.route('/webhook')
@limiter.exempt  # No rate limit
def webhook():
    ...
```

---

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [Flask-Limiter](https://flask-limiter.readthedocs.io/)
- [Structured Logging Best Practices](https://www.kartar.net/2015/12/structured-logging/)

