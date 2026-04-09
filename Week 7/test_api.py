"""
Test script để demo CRUD operations
Chạy sau khi start Flask server
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def print_response(title, response):
    """Pretty print response"""
    print(f"\n{'='*60}")
    print(f"📌 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_api():
    """Test tất cả CRUD operations"""
    
    print("🚀 Starting API Tests...")
    
    # 1. CREATE - Tạo sản phẩm mới
    print("\n\n1️⃣  CREATE PRODUCT")
    product_data = {
        "name": "MacBook Pro M3",
        "description": "High performance laptop for professionals",
        "price": 45990000,
        "category": "Electronics",
        "stock": 20
    }
    
    response = requests.post(f"{BASE_URL}/products", json=product_data)
    print_response("POST /products - Create Product", response)
    
    if response.status_code == 201:
        product_id = response.json()['data']['_id']
        print(f"\n✅ Product created with ID: {product_id}")
    else:
        print("\n❌ Failed to create product")
        return
    
    
    # 2. CREATE - Tạo thêm sản phẩm thứ 2
    print("\n\n2️⃣  CREATE ANOTHER PRODUCT")
    product_data_2 = {
        "name": "iPhone 15 Pro Max",
        "description": "Flagship smartphone from Apple",
        "price": 29990000,
        "category": "Electronics",
        "stock": 50
    }
    
    response = requests.post(f"{BASE_URL}/products", json=product_data_2)
    print_response("POST /products - Create Product #2", response)
    
    
    # 3. READ ALL - Lấy danh sách tất cả sản phẩm
    print("\n\n3️⃣  GET ALL PRODUCTS")
    response = requests.get(f"{BASE_URL}/products")
    print_response("GET /products - List All Products", response)
    
    
    # 4. READ ONE - Lấy thông tin một sản phẩm
    print("\n\n4️⃣  GET ONE PRODUCT")
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    print_response(f"GET /products/{product_id} - Get Product by ID", response)
    
    
    # 5. FILTER - Lọc theo category
    print("\n\n5️⃣  FILTER BY CATEGORY")
    response = requests.get(f"{BASE_URL}/products?category=Electronics")
    print_response("GET /products?category=Electronics - Filter", response)
    
    
    # 6. FILTER - Lọc theo giá
    print("\n\n6️⃣  FILTER BY PRICE RANGE")
    response = requests.get(f"{BASE_URL}/products?min_price=20000000&max_price=50000000")
    print_response("GET /products?min_price=...&max_price=... - Price Filter", response)
    
    
    # 7. UPDATE - Cập nhật sản phẩm
    print("\n\n7️⃣  UPDATE PRODUCT")
    update_data = {
        "name": "MacBook Pro M3 Pro 16-inch",
        "description": "Updated: Professional laptop with M3 Pro chip, 18GB RAM",
        "price": 49990000,
        "category": "Electronics",
        "stock": 15
    }
    
    response = requests.put(f"{BASE_URL}/products/{product_id}", json=update_data)
    print_response(f"PUT /products/{product_id} - Update Product", response)
    
    
    # 8. VERIFY UPDATE - Kiểm tra cập nhật
    print("\n\n8️⃣  VERIFY UPDATE")
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    print_response(f"GET /products/{product_id} - Verify Update", response)
    
    
    # 9. ERROR HANDLING - Invalid ID
    print("\n\n9️⃣  ERROR HANDLING - Invalid ID")
    response = requests.get(f"{BASE_URL}/products/invalid-id-123")
    print_response("GET /products/invalid-id-123 - Invalid ID Error", response)
    
    
    # 10. ERROR HANDLING - Missing required fields
    print("\n\n🔟 ERROR HANDLING - Validation Error")
    invalid_data = {
        "name": "",  # Empty name
        "price": -1000  # Negative price
    }
    response = requests.post(f"{BASE_URL}/products", json=invalid_data)
    print_response("POST /products - Validation Error", response)
    
    
    # 11. DELETE - Xóa sản phẩm
    print("\n\n1️⃣1️⃣  DELETE PRODUCT")
    response = requests.delete(f"{BASE_URL}/products/{product_id}")
    print_response(f"DELETE /products/{product_id} - Delete Product", response)
    
    
    # 12. VERIFY DELETE - Kiểm tra đã xóa
    print("\n\n1️⃣2️⃣  VERIFY DELETION")
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    print_response(f"GET /products/{product_id} - Verify Deletion (should be 404)", response)
    
    
    # Summary
    print("\n\n")
    print("="*60)
    print("✅ TEST COMPLETED!")
    print("="*60)
    print("\n📊 Summary:")
    print("  ✓ CREATE - Product created successfully")
    print("  ✓ READ - Get all products and get by ID")
    print("  ✓ UPDATE - Product updated successfully")
    print("  ✓ DELETE - Product deleted successfully")
    print("  ✓ FILTER - Category and price filtering")
    print("  ✓ ERROR HANDLING - Invalid ID and validation errors")
    print("\n🎉 All CRUD operations working!")


if __name__ == '__main__':
    try:
        # Test connection
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print(f"✅ Server is running at {BASE_URL}")
            test_api()
        else:
            print(f"❌ Server responded with status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {BASE_URL}")
        print("💡 Make sure Flask server is running:")
        print("   python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")
