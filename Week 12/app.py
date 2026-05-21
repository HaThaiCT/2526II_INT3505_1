from flask import Flask, render_template, request, redirect, url_for, jsonify, g
import sqlite3
import uuid
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'week12.db')

app = Flask(__name__)
app.secret_key = 'devportal-demo-secret'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    cur = db.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS developers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            api_key TEXT UNIQUE,
            tier TEXT,
            created_at TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS call_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            developer_id INTEGER,
            path TEXT,
            status_code INTEGER,
            timestamp TEXT,
            FOREIGN KEY(developer_id) REFERENCES developers(id)
        )
    ''')
    db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def create_developer(name, email, tier='free'):
    db = get_db()
    api_key = str(uuid.uuid4())
    created_at = datetime.datetime.utcnow().isoformat()
    cur = db.cursor()
    cur.execute('INSERT INTO developers (name,email,api_key,tier,created_at) VALUES (?,?,?,?,?)',
                (name, email, api_key, tier, created_at))
    db.commit()
    return api_key

def find_developer_by_key(key):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM developers WHERE api_key=?', (key,))
    return cur.fetchone()

def log_call(developer_id, path, status_code):
    db = get_db()
    cur = db.cursor()
    cur.execute('INSERT INTO call_logs (developer_id,path,status_code,timestamp) VALUES (?,?,?,?)',
                (developer_id, path, status_code, datetime.datetime.utcnow().isoformat()))
    db.commit()

def calls_this_month(dev_id):
    db = get_db()
    cur = db.cursor()
    now = datetime.datetime.utcnow()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    cur.execute('SELECT COUNT(*) as cnt FROM call_logs WHERE developer_id=? AND timestamp>=?', (dev_id, start))
    return cur.fetchone()['cnt']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/sandbox')
def sandbox():
    return render_template('sandbox.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    tier = request.form.get('tier') or 'free'
    try:
        api_key = create_developer(name, email, tier)
    except sqlite3.IntegrityError:
        dev = get_db().execute('SELECT * FROM developers WHERE email=?', (email,)).fetchone()
        api_key = dev['api_key']
    return render_template('registered.html', api_key=api_key, tier=tier)

@app.route('/api/demo')
def api_demo():
    key = request.headers.get('X-API-Key') or request.args.get('api_key')
    if not key:
        return jsonify({'error': 'missing api key'}), 401
    dev = find_developer_by_key(key)
    if not dev:
        return jsonify({'error': 'invalid api key'}), 403
    dev_id = dev['id']
    # Monetization simulation: free tier 100 calls/month
    free_limit = 100
    calls = calls_this_month(dev_id)
    price_per_call = 0.01
    headers = {}
    if dev['tier'] != 'free' and calls >= free_limit:
        headers['X-Billing-Mode'] = 'pay-per-call'
        headers['X-Price'] = f'{price_per_call:.2f}'
    status_code = 200
    response = jsonify({'message': 'Hello from Demo API', 'calls_this_month': calls})
    log_call(dev_id, '/api/demo', status_code)
    return (response, status_code, headers)

@app.route('/admin/kpis')
def admin_kpis():
    db = get_db()
    cur = db.cursor()
    dev_count = cur.execute('SELECT COUNT(*) as c FROM developers').fetchone()['c']
    total_calls = cur.execute('SELECT COUNT(*) as c FROM call_logs').fetchone()['c']
    errors = cur.execute('SELECT COUNT(*) as c FROM call_logs WHERE status_code>=400').fetchone()['c']
    error_rate = (errors / total_calls * 100) if total_calls else 0
    return jsonify({'developers': dev_count, 'total_calls': total_calls, 'error_rate_percent': round(error_rate,2)})

if __name__ == '__main__':
    # Ensure DB exists
    if not os.path.exists(DB_PATH):
        with app.app_context():
            init_db()
    app.run(host='0.0.0.0', port=5002, debug=True)
