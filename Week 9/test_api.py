"""
Test Suite cho Payment API (v1 và v2)
Test deprecation headers, conversion, và functionality
"""

import sys
import unittest
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_test_header(message):
    """Print styled test section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_warning(message):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


class TestAPIGeneral(unittest.TestCase):
    """Test general API endpoints"""
    
    def test_01_home_endpoint(self):
        """Test home endpoint returns API info"""
        print_info("Testing home endpoint...")
        response = requests.get(f"{BASE_URL}/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('name', data)
        self.assertIn('versions', data)
        self.assertIn('v1', data['versions'])
        self.assertIn('v2', data['versions'])
        
        print_success(f"Home endpoint OK - Name: {data['name']}")
    
    def test_02_migration_guide(self):
        """Test migration guide endpoint"""
        print_info("Testing migration guide endpoint...")
        response = requests.get(f"{BASE_URL}/migration-guide")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('title', data)
        self.assertIn('breaking_changes', data)
        self.assertIn('migration_steps', data)
        
        print_success("Migration guide available")
        print_info(f"Breaking changes: {len(data.get('breaking_changes', []))}")


class TestAPIv1Deprecated(unittest.TestCase):
    """Test v1 API endpoints (deprecated)"""
    
    @classmethod
    def setUpClass(cls):
        print_test_header("Testing v1 API (DEPRECATED)")
    
    def test_01_v1_docs_has_deprecation_headers(self):
        """Test v1 docs returns deprecation headers"""
        print_info("Testing v1 deprecation headers...")
        response = requests.get(f"{BASE_URL}/api/v1/docs")
        
        self.assertEqual(response.status_code, 200)
        
        # Check deprecation headers
        self.assertIn('Deprecation', response.headers)
        self.assertEqual(response.headers['Deprecation'], 'true')
        
        self.assertIn('Sunset', response.headers)
        print_warning(f"V1 Sunset Date: {response.headers['Sunset']}")
        
        self.assertIn('X-API-Warn', response.headers)
        print_warning(f"Warning: {response.headers['X-API-Warn']}")
        
        print_success("Deprecation headers present")
    
    def test_02_v1_create_payment(self):
        """Test creating payment with v1 format"""
        print_info("Testing v1 create payment...")
        
        payload = {
            "amount": 100.00,
            "currency": "USD",
            "customer_id": "CUST_TEST_001",
            "customer_email": "test@example.com",
            "method": "card"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/payments",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('deprecation_warning', data)
        
        # Save payment ID for later tests
        self.__class__.v1_payment_id = data['data']['_id']
        
        print_success(f"v1 payment created: {self.__class__.v1_payment_id}")
        print_warning(f"Deprecation warning: {data['deprecation_warning'][:50]}...")
    
    def test_03_v1_list_payments(self):
        """Test listing payments with v1"""
        print_info("Testing v1 list payments...")
        
        response = requests.get(f"{BASE_URL}/api/v1/payments")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
        
        print_success(f"v1 payments listed: {data['count']} payments")
    
    def test_04_v1_get_payment(self):
        """Test getting single payment with v1"""
        if not hasattr(self.__class__, 'v1_payment_id'):
            self.skipTest("No payment ID from creation test")
        
        print_info("Testing v1 get payment...")
        
        response = requests.get(
            f"{BASE_URL}/api/v1/payments/{self.__class__.v1_payment_id}"
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['_id'], self.__class__.v1_payment_id)
        
        print_success(f"v1 payment retrieved")


class TestAPIv2Current(unittest.TestCase):
    """Test v2 API endpoints (current)"""
    
    @classmethod
    def setUpClass(cls):
        print_test_header("Testing v2 API (CURRENT)")
    
    def test_01_v2_docs_no_deprecation(self):
        """Test v2 docs doesn't have deprecation headers"""
        print_info("Testing v2 docs (should not be deprecated)...")
        
        response = requests.get(f"{BASE_URL}/api/v2/docs")
        
        self.assertEqual(response.status_code, 200)
        
        # v2 should NOT have deprecation headers
        self.assertNotIn('Deprecation', response.headers)
        
        data = response.json()
        self.assertEqual(data['status'], 'CURRENT')
        
        print_success("v2 is current (not deprecated)")
    
    def test_02_v2_create_payment(self):
        """Test creating payment with v2 format"""
        print_info("Testing v2 create payment...")
        
        payload = {
            "amount": {
                "value": 200.00,
                "currency": "USD"
            },
            "customer": {
                "id": "CUST_TEST_002",
                "email": "test2@example.com",
                "name": "Test User 2",
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
                "order_id": "ORD-123",
                "source": "web"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v2/payments",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Idempotency-Key": f"test-{datetime.now().timestamp()}"
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertEqual(data['version'], '2.0.0')
        
        # Save payment ID
        self.__class__.v2_payment_id = data['data']['_id']
        
        print_success(f"v2 payment created: {self.__class__.v2_payment_id}")
    
    def test_03_v2_list_payments(self):
        """Test listing payments with v2"""
        print_info("Testing v2 list payments...")
        
        response = requests.get(f"{BASE_URL}/api/v2/payments")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
        
        print_success(f"v2 payments listed: {data['count']} payments")
    
    def test_04_v2_list_with_filters(self):
        """Test v2 list with query parameters"""
        print_info("Testing v2 list with filters...")
        
        response = requests.get(
            f"{BASE_URL}/api/v2/payments?status=pending&currency=USD"
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        
        print_success(f"v2 filtered list: {data['count']} payments")
    
    def test_05_v2_get_payment(self):
        """Test getting single payment with v2"""
        if not hasattr(self.__class__, 'v2_payment_id'):
            self.skipTest("No payment ID from creation test")
        
        print_info("Testing v2 get payment...")
        
        response = requests.get(
            f"{BASE_URL}/api/v2/payments/{self.__class__.v2_payment_id}"
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['_id'], self.__class__.v2_payment_id)
        
        # Check nested structure
        self.assertIn('amount', data['data'])
        self.assertIn('value', data['data']['amount'])
        self.assertIn('customer', data['data'])
        self.assertIn('payment_method', data['data'])
        
        print_success("v2 payment retrieved with nested structure")
    
    def test_06_v2_update_payment(self):
        """Test updating payment with v2"""
        if not hasattr(self.__class__, 'v2_payment_id'):
            self.skipTest("No payment ID from creation test")
        
        print_info("Testing v2 update payment...")
        
        payload = {
            "status": "completed",
            "metadata": {
                "completed_by": "test_suite"
            }
        }
        
        response = requests.put(
            f"{BASE_URL}/api/v2/payments/{self.__class__.v2_payment_id}",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['status'], 'completed')
        
        print_success("v2 payment updated")
    
    def test_07_v2_refund_payment(self):
        """Test refunding payment (NEW in v2)"""
        if not hasattr(self.__class__, 'v2_payment_id'):
            self.skipTest("No payment ID from creation test")
        
        print_info("Testing v2 refund payment (NEW feature)...")
        
        payload = {
            "amount": 100.00,
            "reason": "Test refund"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v2/payments/{self.__class__.v2_payment_id}/refund",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['status'], 'refunded')
        self.assertIn('refund', data['data'])
        
        print_success("v2 refund successful (NEW v2 feature)")
    
    def test_08_v2_payment_history(self):
        """Test getting payment history (NEW in v2)"""
        if not hasattr(self.__class__, 'v2_payment_id'):
            self.skipTest("No payment ID from creation test")
        
        print_info("Testing v2 payment history (NEW feature)...")
        
        response = requests.get(
            f"{BASE_URL}/api/v2/payments/{self.__class__.v2_payment_id}/history"
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['success'])
        self.assertIn('history', data)
        self.assertIsInstance(data['history'], list)
        
        print_success(f"v2 history retrieved: {len(data['history'])} events (NEW v2 feature)")


class TestCompatibility(unittest.TestCase):
    """Test compatibility between v1 and v2"""
    
    @classmethod
    def setUpClass(cls):
        print_test_header("Testing v1 ↔ v2 Compatibility")
    
    def test_01_v1_can_read_v2_data(self):
        """Test that v1 can read payments created by v2"""
        print_info("Testing v1 reading v2 data...")
        
        # Create payment with v2
        v2_payload = {
            "amount": {"value": 300.00, "currency": "EUR"},
            "customer": {"id": "CUST_COMPAT", "email": "compat@test.com"},
            "payment_method": {"type": "bank_transfer"}
        }
        
        v2_response = requests.post(
            f"{BASE_URL}/api/v2/payments",
            json=v2_payload
        )
        self.assertEqual(v2_response.status_code, 201)
        payment_id = v2_response.json()['data']['_id']
        
        # Read with v1
        v1_response = requests.get(f"{BASE_URL}/api/v1/payments/{payment_id}")
        self.assertEqual(v1_response.status_code, 200)
        
        v1_data = v1_response.json()['data']
        self.assertEqual(v1_data['amount'], 300.00)
        self.assertEqual(v1_data['currency'], 'EUR')
        
        print_success("v1 can read v2 data (backward compatible)")
    
    def test_02_v2_can_read_v1_data(self):
        """Test that v2 can read payments created by v1"""
        print_info("Testing v2 reading v1 data...")
        
        # Create payment with v1
        v1_payload = {
            "amount": 400.00,
            "currency": "VND",
            "customer_id": "CUST_COMPAT_2",
            "method": "wallet"
        }
        
        v1_response = requests.post(
            f"{BASE_URL}/api/v1/payments",
            json=v1_payload
        )
        self.assertEqual(v1_response.status_code, 201)
        payment_id = v1_response.json()['data']['_id']
        
        # Read with v2
        v2_response = requests.get(f"{BASE_URL}/api/v2/payments/{payment_id}")
        self.assertEqual(v2_response.status_code, 200)
        
        v2_data = v2_response.json()['data']
        self.assertEqual(v2_data['amount']['value'], 400.00)
        self.assertEqual(v2_data['amount']['currency'], 'VND')
        
        print_success("v2 can read v1 data (forward compatible)")


def run_tests():
    """Run all test suites"""
    print_test_header("Payment API Test Suite - v1 & v2")
    print_info(f"Testing API at: {BASE_URL}")
    print_info("Make sure the API is running before running tests!\n")
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print_success("✓ API is running and accessible\n")
        else:
            print_warning(f"⚠ API returned status {response.status_code}\n")
    except requests.exceptions.ConnectionError:
        print(f"{Colors.FAIL}✗ Cannot connect to API at {BASE_URL}{Colors.ENDC}")
        print(f"{Colors.FAIL}Please start the API first with: python app.py{Colors.ENDC}\n")
        sys.exit(1)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes in order
    suite.addTests(loader.loadTestsFromTestCase(TestAPIGeneral))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIv1Deprecated))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIv2Current))
    suite.addTests(loader.loadTestsFromTestCase(TestCompatibility))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print_test_header("Test Summary")
    print(f"{Colors.OKGREEN}✓ Tests passed: {result.testsRun - len(result.failures) - len(result.errors)}{Colors.ENDC}")
    if result.failures:
        print(f"{Colors.FAIL}✗ Tests failed: {len(result.failures)}{Colors.ENDC}")
    if result.errors:
        print(f"{Colors.FAIL}✗ Tests errored: {len(result.errors)}{Colors.ENDC}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
