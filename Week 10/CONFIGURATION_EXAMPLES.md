# Configuration Examples for Logging & Monitoring

Các ví dụ cấu hình cho các tình huống khác nhau.

## 1. Logging Configurations

### Development Setup

```python
import logging

def setup_logging_dev():
    """Development logging - verbose, console only"""
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)
    
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

### Production Setup (Centralized Logging)

```python
import logging
from pythonjsonlogger import jsonlogger

def setup_logging_prod():
    """Production logging - JSON to file + remote"""
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)
    
    # File handler - JSON
    file_handler = logging.FileHandler('app.log')
    json_formatter = jsonlogger.JsonFormatter()
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)
    
    # Syslog handler (Linux/Mac)
    # import logging.handlers
    # syslog_handler = logging.handlers.SysLogHandler('/dev/log')
    # logger.addHandler(syslog_handler)
    
    return logger
```

### Log Rotation

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging_rotation():
    """Logging with rotation"""
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)
    
    # Rotate when file reaches 10MB, keep 5 backups
    handler = RotatingFileHandler(
        'app.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

### Time-based Rotation

```python
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logging_timed_rotation():
    """Rotate logs daily"""
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)
    
    # Rotate daily at midnight
    handler = TimedRotatingFileHandler(
        'app.log',
        when='midnight',
        interval=1,
        backupCount=30  # Keep 30 days
    )
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

---

## 2. Rate Limiting Configurations

### Tiered Rate Limiting

```python
from flask_limiter import Limiter

# Different limits for different user types
limiter = Limiter(app=app, key_func=get_remote_address)

# Public endpoints - strict
@app.route('/api/public/search')
@limiter.limit("10 per minute")
def public_search():
    return search_results()

# Standard endpoints - moderate
@app.route('/api/books')
@limiter.limit("100 per hour")
def get_books():
    return books()

# Premium endpoints - generous
@app.route('/api/premium/analytics')
@limiter.limit("1000 per hour")
def premium_analytics():
    return analytics()

# Admin endpoints - unlimited
@app.route('/api/admin/config')
@limiter.exempt
def admin_config():
    return config()
```

### User-based Rate Limiting

```python
from flask import session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def get_user_key():
    """Rate limit by user ID or IP"""
    if 'user_id' in session:
        return f"user_{session['user_id']}"
    return get_remote_address()

limiter = Limiter(app=app, key_func=get_user_key)

# Usage
@app.route('/api/data')
@limiter.limit("100 per hour")
def get_data():
    return data()
```

### Redis-backed Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Production setup with Redis
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["200 per day", "50 per hour"]
)
```

### Dynamic Rate Limiting

```python
from flask_limiter import Limiter
from flask import request

limiter = Limiter(app=app, key_func=lambda: request.remote_addr)

@app.route('/api/resource')
def dynamic_limit():
    # Check user type and apply different limits
    user_type = request.args.get('type', 'free')
    
    if user_type == 'premium':
        return "High limit applied"
    else:
        return "Standard limit applied"
```

---

## 3. Prometheus Configurations

### Custom Metrics Configuration

```python
from prometheus_client import Counter, Histogram, Gauge, Summary

# Fine-grained metrics
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['operation'],  # INSERT, SELECT, UPDATE, DELETE
    buckets=(0.01, 0.05, 0.1, 0.5, 1, 2, 5)
)

api_cache_hits = Counter(
    'api_cache_hits_total',
    'Cache hits',
    ['endpoint']
)

api_cache_misses = Counter(
    'api_cache_misses_total',
    'Cache misses',
    ['endpoint']
)

queue_size = Gauge(
    'job_queue_size',
    'Pending jobs in queue'
)

# Usage
@app.route('/books')
def get_books():
    # Check cache
    cache_key = 'all_books'
    books = cache.get(cache_key)
    
    if books:
        api_cache_hits.labels(endpoint='/books').inc()
    else:
        api_cache_misses.labels(endpoint='/books').inc()
        start = time.time()
        books = db.query("SELECT * FROM books")
        duration = time.time() - start
        db_query_duration.labels(operation='SELECT').observe(duration)
    
    return jsonify(books=books)
```

### High Cardinality Prevention

```python
from prometheus_client import Counter

# BAD - Unbounded cardinality
# Every user_id creates new metric
request_by_user = Counter(
    'requests_by_user',
    'Requests',
    ['user_id']  # ❌ Can be millions of unique values
)

# GOOD - Bounded cardinality
request_by_tier = Counter(
    'requests_by_tier',
    'Requests',
    ['user_tier']  # ✓ Only free/premium/enterprise
)

request_by_region = Counter(
    'requests_by_region',
    'Requests',
    ['region']  # ✓ Limited number of regions
)
```

---

## 4. Structured Logging Patterns

### Context-aware Logging

```python
import logging
from contextvars import ContextVar

# Context variable to track request
request_id = ContextVar('request_id', default=None)

class ContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id.get()
        return True

# Setup
logger = logging.getLogger('app')
logger.addFilter(ContextFilter())

# Usage
@app.route('/api/data')
def get_data():
    from uuid import uuid4
    req_id = str(uuid4())
    request_id.set(req_id)
    
    logger.info("Request started")
    # All logs in this context will include request_id
    data = fetch_data()
    logger.info("Request completed")
    
    return data
```

### Error Logging with Context

```python
def log_error_context(exception, context=None):
    """Log errors with full context"""
    logger.error(
        "An error occurred",
        exc_info=True,
        extra={
            'error_type': type(exception).__name__,
            'error_message': str(exception),
            'context': context or {},
            'user_id': session.get('user_id'),
            'endpoint': request.endpoint,
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.args),
        }
    )
```

---

## 5. Combined Setup Examples

### Minimal Production Setup

```python
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_client import Counter, generate_latest, REGISTRY
import logging

app = Flask(__name__)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)

# Metrics
requests_total = Counter('requests_total', 'Total requests', ['method', 'status'])

@app.route('/health')
def health():
    return {'status': 'ok'}

@app.route('/metrics')
def metrics():
    return generate_latest(REGISTRY)

@app.route('/api/data')
@limiter.limit("100 per hour")
def get_data():
    logger.info("Data requested")
    return {'data': 'example'}
```

### Complete Enterprise Setup

```python
import logging
from logging.handlers import RotatingFileHandler, SysLogHandler
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import time

app = Flask(__name__)

# Advanced Logging
def setup_logging():
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'app.log',
        maxBytes=52428800,  # 50MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(file_handler)
    
    # Syslog handler
    try:
        syslog_handler = SysLogHandler('/dev/log')
        logger.addHandler(syslog_handler)
    except:
        pass  # Windows doesn't have syslog
    
    return logger

logger = setup_logging()

# Advanced Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379",
    default_limits=["200 per day", "50 per hour"],
    in_memory_fallback_enabled=True
)

# Advanced Metrics
requests_total = Counter(
    'requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'request_duration_seconds',
    'Request duration',
    ['endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10)
)

active_connections = Gauge(
    'active_connections',
    'Active connections'
)

def track_metrics(f):
    def wrapper(*args, **kwargs):
        active_connections.inc()
        start = time.time()
        try:
            result = f(*args, **kwargs)
            status = 200
            return result
        except Exception as e:
            status = 500
            logger.error(f"Error: {e}", exc_info=True)
            raise
        finally:
            duration = time.time() - start
            request_duration.labels(endpoint=request.endpoint).observe(duration)
            requests_total.labels(
                method=request.method,
                endpoint=request.endpoint,
                status=status
            ).inc()
            active_connections.dec()
    
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/health')
def health():
    return {'status': 'healthy'}

@app.route('/metrics')
def metrics():
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain'}

@app.route('/api/data')
@limiter.limit("100 per hour")
@track_metrics
def get_data():
    logger.info("Data endpoint accessed")
    return {'data': 'example'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 6. Environment-based Configuration

```python
import os

class Config:
    """Base configuration"""
    LOGGING_LEVEL = 'INFO'
    RATE_LIMIT_STORAGE = 'memory://'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOGGING_LEVEL = 'DEBUG'
    RATE_LIMIT_STORAGE = 'memory://'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOGGING_LEVEL = 'WARNING'
    RATE_LIMIT_STORAGE = 'redis://localhost:6379'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    RATE_LIMIT_ENABLED = False
    LOGGING_LEVEL = 'DEBUG'

# Usage
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

environment = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[environment])
```

---

## 7. Docker Deployment

### Dockerfile with Logging

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

# Create log directory
RUN mkdir -p /var/log/app

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "app.py"]
```

### Docker Compose with Prometheus

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./logs:/var/log/app
    environment:
      - FLASK_ENV=production

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus_data:
  grafana_data:
```

