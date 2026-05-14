# QUICKSTART - Library API with Logging & Monitoring

Hướng dẫn nhanh để chạy Library API với logging, monitoring và rate limiting.

## ⚡ 5 Phút Setup

### 1. Cài đặt Python Packages (1 phút)

```bash
pip install -r requirements.txt
```

### 2. Chạy Flask App (30 giây)

```bash
python app.py
```

Output:
```
 * Running on http://0.0.0.0:5000
```

### 3. Test API (1 phút)

```bash
# Health check
curl http://localhost:5000/health

# Get all books
curl http://localhost:5000/books

# View metrics
curl http://localhost:5000/metrics
```

### 4. View Logs (1 phút)

```bash
# Open log file
type library_api.log

# Or monitor in real-time (PowerShell)
Get-Content library_api.log -Tail 10 -Wait
```

---

## 🧪 Test API Endpoints

### Run Full Test Suite

```bash
python test_api.py
```

### Manual Testing

#### 1. Get All Books
```bash
curl http://localhost:5000/books
```

Response:
```json
{
  "books": [
    {"id": "1", "title": "Clean Code", "author": "Robert C. Martin", "available": 5},
    {"id": "2", "title": "Design Patterns", "author": "Gang of Four", "available": 3}
  ]
}
```

#### 2. Create New Book
```bash
curl -X POST http://localhost:5000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Programming",
    "author": "Mark Lutz",
    "available": 3
  }'
```

#### 3. Borrow a Book
```bash
curl -X POST http://localhost:5000/books/1/borrow
```

#### 4. Get Metrics (Prometheus)
```bash
curl http://localhost:5000/metrics
```

---

## 📊 Monitoring with Prometheus

### Option 1: Quick Prometheus Setup (Windows)

1. **Download Prometheus:**
   - Visit https://prometheus.io/download/
   - Download `prometheus-X.Y.Z.windows-amd64.zip`
   - Extract to `C:\prometheus`

2. **Copy Configuration:**
   ```bash
   # Copy prometheus.yml from this directory to C:\prometheus\
   ```

3. **Start Prometheus:**
   ```bash
   cd C:\prometheus
   .\prometheus.exe --config.file=prometheus.yml
   ```

4. **Access Prometheus:**
   - Open http://localhost:9090
   - Go to "Graph" tab
   - Query: `rate(library_api_requests_total[1m])`

### Option 2: Docker (If available)

```bash
# Start Prometheus
docker run -d \
  -v ${PWD}/prometheus.yml:/etc/prometheus/prometheus.yml \
  -p 9090:9090 \
  prom/prometheus

# Access at http://localhost:9090
```

---

## 📈 Grafana Dashboard (Optional)

### 1. Start Grafana

```bash
# Windows - Download from https://grafana.com/grafana/download
# Extract and run grafana-server.exe

# Or Docker
docker run -d -p 3000:3000 grafana/grafana
```

### 2. Configure Data Source

- Visit http://localhost:3000
- Login: admin / admin
- Add Data Source → Prometheus
- URL: http://localhost:9090

### 3. Import Dashboard

Create new dashboard with panels:

**Panel 1: Request Rate**
```
Query: rate(library_api_requests_total[1m])
```

**Panel 2: Response Time (95th percentile)**
```
Query: histogram_quantile(0.95, library_api_request_duration_seconds_bucket)
```

**Panel 3: Active Requests**
```
Query: library_api_active_requests
```

---

## 📝 Log Analysis

### View Latest Logs

```bash
# Last 20 lines
Get-Content library_api.log -Tail 20

# Follow logs in real-time (PowerShell)
Get-Content library_api.log -Tail 10 -Wait

# Search for errors
Select-String -Path library_api.log -Pattern "ERROR"

# Filter by endpoint
Select-String -Path library_api.log -Pattern "/books" | Select-Object -Last 10
```

### Parse JSON Logs

```python
import json

with open('library_api.log', 'r') as f:
    for line in f:
        log_entry = json.loads(line)
        print(f"[{log_entry['timestamp']}] {log_entry['level']}: {log_entry['message']}")
```

---

## 🚦 Rate Limiting Examples

### Test Rate Limiting

```bash
# Make 40 requests (limit is 30/min)
for /l %i in (1,1,40) do (
  curl http://localhost:5000/books
  timeout /t 1 /nobreak
)
```

### Monitor Rate Limit Events

```bash
# Check for 429 responses
Select-String -Path library_api.log -Pattern "429"

# View rate limit exceeded logs
Select-String -Path library_api.log -Pattern "rate_limit"
```

---

## 🔍 Common Metrics to Monitor

### Business Metrics

```
# Total requests by endpoint
sum(rate(library_api_requests_total[1m])) by (endpoint)

# Success vs Error rate
sum(rate(library_api_requests_total{status=~"2.."}[1m])) vs 
sum(rate(library_api_requests_total{status=~"5.."}[1m]))
```

### Performance Metrics

```
# Average response time
avg(rate(library_api_request_duration_seconds_sum[5m])) 
/ 
avg(rate(library_api_request_duration_seconds_count[5m]))

# 99th percentile latency
histogram_quantile(0.99, library_api_request_duration_seconds_bucket)

# Active requests
library_api_active_requests
```

### Operational Metrics

```
# Rate limit violations per minute
rate(library_api_rate_limit_exceeded_total[1m])

# Total books in system
library_api_books_count

# Error rate by status
sum(rate(library_api_requests_total{status=~"5.."}[1m])) by (status)
```

---

## 🐛 Troubleshooting

### App won't start

```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process on port 5000 (Windows)
taskkill /PID <PID> /F
```

### Logs not being written

```bash
# Check file permissions
icacls library_api.log

# Check disk space
powershell -Command "Get-Item library_api.log | Select-Object Length"
```

### Prometheus not scraping metrics

```bash
# Check if metrics endpoint works
curl http://localhost:5000/metrics

# Verify prometheus.yml config
type prometheus.yml

# Check Prometheus targets at http://localhost:9090/targets
```

### Rate limiting not working

```bash
# Verify endpoint has decorator
grep -n "@limiter.limit" app.py

# Check rate limit headers
curl -i http://localhost:5000/books
# Look for X-RateLimit-* headers
```

---

## 📚 File Structure

```
Week 10/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── test_api.py                     # Test suite
├── prometheus.yml                  # Prometheus configuration
├── README.md                       # Full documentation
├── LOGGING_MONITORING_GUIDE.md    # Detailed guide
├── QUICKSTART.md                   # This file
└── library_api.log                 # Generated log file
```

---

## 🎯 Next Steps

1. **✓ Run the app** - `python app.py`
2. **✓ Test endpoints** - `python test_api.py`
3. **✓ Check logs** - `type library_api.log`
4. **✓ View metrics** - Visit http://localhost:5000/metrics
5. **⚪ Setup Prometheus** (optional)
6. **⚪ Setup Grafana** (optional)

---

## 💡 Tips

- **Real-time logs:** Use PowerShell's `Get-Content ... -Wait` for live monitoring
- **JSON parsing:** Use `jq` or similar tools to filter logs
- **Rate limit testing:** Use Apache Bench (`ab`) or similar tools for load testing
- **Metrics retention:** Prometheus keeps 15 days by default, adjust in config if needed

---

## 📞 Support

For detailed information:
- See [README.md](README.md) for full documentation
- See [LOGGING_MONITORING_GUIDE.md](LOGGING_MONITORING_GUIDE.md) for deep dive
- Check [Prometheus Docs](https://prometheus.io/docs/)
- Check [Flask-Limiter Docs](https://flask-limiter.readthedocs.io/)
