#!/usr/bin/env python3
"""
Script để kiểm tra API và hiển thị đồ thị
"""
import requests
import json
import sys
import webbrowser
import time
from pathlib import Path

# API endpoint
API_URL = "http://localhost:8000/estimate"

# Test data
TEST_DATA = {
    "text": """
    Requirement Specification:
    1. User Registration:
       - Users should be able to create an account with email and password
       - Users should receive a confirmation email after registration
       - System should validate email format and password strength

    2. User Authentication:
       - Users should be able to log in using their email and password
       - System should provide password reset functionality
       - System should lock accounts after 5 failed login attempts

    3. Product Management:
       - Users should be able to add, edit, and delete products
       - Each product should have name, description, price, and category
       - System should support product image uploads
       - Products should be searchable by name, category, and price range

    4. Shopping Cart:
       - Users should be able to add products to a shopping cart
       - Users should be able to adjust quantities or remove items
       - Shopping cart should persist across sessions
       - System should calculate total price including taxes and discounts

    5. Checkout and Payment:
       - Users should be able to enter shipping details
       - System should support multiple payment methods (credit card, PayPal)
       - System should send order confirmation emails
       - Users should be able to track order status

    6. Reviews and Ratings:
       - Users should be able to rate products from 1-5 stars
       - Users should be able to write reviews for products
       - System should allow moderation of reviews
       - System should display average rating for each product
    """,
    "method": "weighted_average"
}

# Vietnamese test data
TEST_DATA_VIETNAMESE = {
    "text": """
    Đặc tả yêu cầu:
    1. Đăng ký người dùng:
       - Người dùng có thể tạo tài khoản với email và mật khẩu
       - Người dùng nhận được email xác nhận sau khi đăng ký
       - Hệ thống xác thực định dạng email và độ mạnh của mật khẩu

    2. Xác thực người dùng:
       - Người dùng có thể đăng nhập bằng email và mật khẩu
       - Hệ thống cung cấp chức năng đặt lại mật khẩu
       - Hệ thống khóa tài khoản sau 5 lần đăng nhập thất bại

    3. Quản lý sản phẩm:
       - Người dùng có thể thêm, sửa và xóa sản phẩm
       - Mỗi sản phẩm có tên, mô tả, giá và danh mục
       - Hệ thống hỗ trợ tải lên hình ảnh sản phẩm
       - Sản phẩm có thể tìm kiếm theo tên, danh mục và khoảng giá

    4. Giỏ hàng:
       - Người dùng có thể thêm sản phẩm vào giỏ hàng
       - Người dùng có thể điều chỉnh số lượng hoặc xóa mặt hàng
       - Giỏ hàng được lưu giữ qua các phiên làm việc
       - Hệ thống tính tổng giá bao gồm thuế và giảm giá

    5. Thanh toán:
       - Người dùng có thể nhập thông tin vận chuyển
       - Hệ thống hỗ trợ nhiều phương thức thanh toán (thẻ tín dụng, PayPal)
       - Hệ thống gửi email xác nhận đơn hàng
       - Người dùng có thể theo dõi trạng thái đơn hàng

    6. Đánh giá và xếp hạng:
       - Người dùng có thể xếp hạng sản phẩm từ 1-5 sao
       - Người dùng có thể viết đánh giá cho sản phẩm
       - Hệ thống cho phép kiểm duyệt đánh giá
       - Hệ thống hiển thị đánh giá trung bình cho mỗi sản phẩm
    """,
    "method": "weighted_average"
}

def test_api():
    """Test the API with sample data and open browser"""
    print("Testing API with English requirements...")
    try:
        response = requests.post(API_URL, json=TEST_DATA)
        if response.status_code == 200:
            print("API request successful!")
            data = response.json()
            print(f"Estimated effort: {data['estimation']['total_effort']} person-months")
            
            # Open browser
            webbrowser.open("http://localhost:8000/")
        else:
            print(f"API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Wait a bit for the API to fully start
    print("Waiting for API service to start...")
    time.sleep(2)
    
    # Test the API
    test_api()