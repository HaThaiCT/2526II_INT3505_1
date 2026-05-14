import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_response(title, resp, show_json=True):
    """Print API response"""
    print(f"\n{title}")
    print(f"Status Code: {resp.status_code}")
    if show_json and resp.text:
        try:
            print(f"Response: {json.dumps(resp.json(), indent=2)}")
        except:
            print(f"Response: {resp.text}")

def test_health_check():
    """Test health check endpoint"""
    print_section("1. HEALTH CHECK")
    resp = requests.get(f"{BASE_URL}/health")
    print_response("GET /health", resp)
    return resp.status_code == 200

def test_get_all_books():
    """Test get all books"""
    print_section("2. GET ALL BOOKS")
    resp = requests.get(f"{BASE_URL}/books")
    print_response("GET /books", resp)
    return resp.status_code == 200

def test_get_single_book():
    """Test get single book"""
    print_section("3. GET SINGLE BOOK")
    resp = requests.get(f"{BASE_URL}/books/1")
    print_response("GET /books/1", resp)
    return resp.status_code == 200

def test_create_book():
    """Test create new book"""
    print_section("4. CREATE NEW BOOK")
    payload = {
        "title": "Python Advanced",
        "author": "Mark Lutz",
        "available": 5
    }
    resp = requests.post(f"{BASE_URL}/books", json=payload)
    print_response("POST /books", resp)
    return resp.status_code == 201

def test_borrow_book():
    """Test borrow book"""
    print_section("5. BORROW BOOK")
    resp = requests.post(f"{BASE_URL}/books/1/borrow")
    print_response("POST /books/1/borrow", resp)
    return resp.status_code == 200

def test_return_book():
    """Test return book"""
    print_section("6. RETURN BOOK")
    resp = requests.post(f"{BASE_URL}/books/1/return")
    print_response("POST /books/1/return", resp)
    return resp.status_code == 200

def test_get_stats():
    """Test get statistics"""
    print_section("7. GET STATISTICS")
    resp = requests.get(f"{BASE_URL}/stats")
    print_response("GET /stats", resp)
    return resp.status_code == 200

def test_delete_book():
    """Test delete book (careful - uses DELETE method)"""
    print_section("8. DELETE BOOK (Demo)")
    # Note: This actually deletes a book, be careful
    resp = requests.delete(f"{BASE_URL}/books/999")  # Non-existent ID
    print_response("DELETE /books/999 (Non-existent)", resp)
    return resp.status_code == 404

def test_not_found():
    """Test 404 error"""
    print_section("9. TEST 404 ERROR")
    resp = requests.get(f"{BASE_URL}/invalid_endpoint")
    print_response("GET /invalid_endpoint", resp)
    return resp.status_code == 404

def test_rate_limiting():
    """Test rate limiting"""
    print_section("10. TEST RATE LIMITING")
    print("\nMaking 35 rapid requests to /books (limit: 30/min)...")
    
    success_count = 0
    rate_limited = 0
    
    for i in range(35):
        resp = requests.get(f"{BASE_URL}/books")
        
        if resp.status_code == 200:
            success_count += 1
            print(f"Request {i+1}: ✓ Success (200)")
        elif resp.status_code == 429:
            rate_limited += 1
            print(f"Request {i+1}: ✗ Rate Limited (429)")
        else:
            print(f"Request {i+1}: ? Unexpected ({resp.status_code})")
        
        time.sleep(0.01)  # Small delay between requests
    
    print(f"\nResults:")
    print(f"  Successful: {success_count}")
    print(f"  Rate Limited: {rate_limited}")
    
    return rate_limited > 0

def test_metrics_endpoint():
    """Test Prometheus metrics"""
    print_section("11. PROMETHEUS METRICS")
    resp = requests.get(f"{BASE_URL}/metrics")
    print(f"Status Code: {resp.status_code}")
    print(f"Content Type: {resp.headers.get('Content-Type', 'N/A')}")
    
    # Show first 500 chars of metrics
    metrics_text = resp.text[:500]
    print(f"\nFirst 500 chars of metrics:")
    print(metrics_text)
    print("...\n")
    
    return resp.status_code == 200

def test_invalid_request():
    """Test invalid request handling"""
    print_section("12. TEST INVALID REQUEST")
    payload = {
        "title": "Incomplete Book"
        # Missing required fields
    }
    resp = requests.post(f"{BASE_URL}/books", json=payload)
    print_response("POST /books (Missing fields)", resp)
    return resp.status_code == 400

def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " " * 12 + "LIBRARY API TEST SUITE" + " " * 24 + "║")
    print("║" + f" Testing: {BASE_URL}".ljust(59) + "║")
    print("║" + f" Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".ljust(59) + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Health Check", test_health_check),
        ("Get All Books", test_get_all_books),
        ("Get Single Book", test_get_single_book),
        ("Create New Book", test_create_book),
        ("Borrow Book", test_borrow_book),
        ("Return Book", test_return_book),
        ("Get Statistics", test_get_stats),
        ("Delete Non-existent Book", test_delete_book),
        ("Test 404 Error", test_not_found),
        ("Rate Limiting", test_rate_limiting),
        ("Prometheus Metrics", test_metrics_endpoint),
        ("Invalid Request", test_invalid_request),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASS" if result else "FAIL"))
        except Exception as e:
            print(f"\n❌ Error in {test_name}: {str(e)}")
            results.append((test_name, "ERROR"))
    
    # Summary
    print_section("TEST SUMMARY")
    print(f"\n{'Test Name':<30} | {'Result':<10}")
    print("-" * 45)
    
    passed = 0
    failed = 0
    errors = 0
    
    for test_name, result in results:
        print(f"{test_name:<30} | {result:<10}")
        if result == "PASS":
            passed += 1
        elif result == "FAIL":
            failed += 1
        else:
            errors += 1
    
    print("-" * 45)
    print(f"{'Total':<30} | {passed + failed + errors:<10}")
    print(f"\n✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"⚠ Errors: {errors}")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error: Cannot connect to {BASE_URL}")
        print("Make sure the Flask app is running:")
        print("  python app.py")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
