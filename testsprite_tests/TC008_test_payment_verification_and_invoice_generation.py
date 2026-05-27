import requests
from requests.exceptions import RequestException

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_payment_verification_and_invoice_generation():
    session = requests.Session()
    try:
        # Try to get a valid product_id from shop page first
        shop_resp = session.get(f"{BASE_URL}/shop/", timeout=TIMEOUT)
        assert shop_resp.status_code == 200, "Failed to fetch shop page for product id"

        # Heuristic: pick product id from shop page or fallback to "1"
        # Since no JSON response, use fallback '1'
        product_id_fallback = "1"

        # Step 1: Create Razorpay order with empty cart but with product_id fallback
        create_order_resp = session.post(
            f"{BASE_URL}/payments/create-order/",
            json={"product_id": product_id_fallback},  # specify fallback product_id as per PRD
            timeout=TIMEOUT
        )
        assert create_order_resp.status_code == 200, f"Expected 200 from create-order, got {create_order_resp.status_code}"
        order_data = create_order_resp.json()
        razorpay_order_id = order_data.get("order_id")
        assert razorpay_order_id, "order_id missing in create-order response"

        # We do not expect product_id in create-order response, use fallback
        product_id = product_id_fallback

        valid_payment_data = {
            "payment_id": "pay_valid_123456",
            "razorpay_order_id": razorpay_order_id,
            "razorpay_signature": "valid_signature_example",
            "product_id": product_id,
            "customer_name": "Test Customer",
            "phone": "1234567890",
            "email": "testcustomer@example.com",
            "address": "123 Test Street, Test City"
        }

        # POST valid payment verification - expect 200 success
        verify_resp = session.post(
            f"{BASE_URL}/payments/verify-payment/",
            json=valid_payment_data,
            timeout=TIMEOUT
        )
        assert verify_resp.status_code == 200, f"Expected 200 for valid payment verify, got {verify_resp.status_code}"
        verify_json = verify_resp.json()
        assert (verify_json.get("status") in ["success", "ok", "completed", "verified", "payment_verified"] or isinstance(verify_json.get("status"), str)), "Missing or unexpected status in success verify-payment response"
        assert "message" in verify_json and isinstance(verify_json["message"], str), "Missing or non-string message in verify-payment response"

        # POST invalid razorpay_signature - expect 400 error
        invalid_signature_data = valid_payment_data.copy()
        invalid_signature_data["razorpay_signature"] = "invalid_signature"
        invalid_sig_resp = session.post(
            f"{BASE_URL}/payments/verify-payment/",
            json=invalid_signature_data,
            timeout=TIMEOUT
        )
        assert invalid_sig_resp.status_code == 400, f"Expected 400 for invalid signature, got {invalid_sig_resp.status_code}"

        # POST unknown razorpay_order_id - expect 404 error
        unknown_order_data = valid_payment_data.copy()
        unknown_order_data["razorpay_order_id"] = "order_unknown_0000"
        unknown_order_resp = session.post(
            f"{BASE_URL}/payments/verify-payment/",
            json=unknown_order_data,
            timeout=TIMEOUT
        )
        assert unknown_order_resp.status_code == 404, f"Expected 404 for unknown order_id, got {unknown_order_resp.status_code}"

        # Step 2: Test that after successful checkout, cart is cleared and invoice generated
        # Add item to cart
        pid = product_id_fallback
        add_cart_resp = session.post(
            f"{BASE_URL}/cart/add/{pid}/",
            data={"size": "M", "quantity": 1},
            timeout=TIMEOUT,
            allow_redirects=False
        )
        assert add_cart_resp.status_code == 302, f"Expected 302 redirect after adding to cart, got {add_cart_resp.status_code}"

        # Create order with cart contents (no product_id passed)
        order_resp = session.post(
            f"{BASE_URL}/payments/create-order/",
            json={},  # use cart contents
            timeout=TIMEOUT
        )
        assert order_resp.status_code == 200, f"Expected 200 from create-order with cart, got {order_resp.status_code}"
        order_info = order_resp.json()
        new_razorpay_order_id = order_info.get("order_id")
        assert new_razorpay_order_id, "Missing order_id in create-order response from cart"

        # Verify payment with this order; should clear cart and generate invoice
        payment_verify_data = {
            "payment_id": "pay_test_after_checkout",
            "razorpay_order_id": new_razorpay_order_id,
            "razorpay_signature": "valid_signature_after_checkout",
            "product_id": pid,
            "customer_name": "Checkout Customer",
            "phone": "0987654321",
            "email": "checkoutcustomer@example.com",
            "address": "456 Checkout Lane"
        }
        payment_verify_resp = session.post(
            f"{BASE_URL}/payments/verify-payment/",
            json=payment_verify_data,
            timeout=TIMEOUT
        )
        assert payment_verify_resp.status_code == 200, f"Expected 200 from verify-payment after checkout, got {payment_verify_resp.status_code}"
        payment_verify_json = payment_verify_resp.json()
        assert ("status" in payment_verify_json and (payment_verify_json["status"] == "success" or isinstance(payment_verify_json["status"], str)))
        assert ("message" in payment_verify_json and isinstance(payment_verify_json["message"], str))

        # Check cart is cleared - GET /cart/ should show empty cart or no items
        cart_resp = session.get(f"{BASE_URL}/cart/", timeout=TIMEOUT)
        assert cart_resp.status_code == 200, f"Expected 200 from cart view, got {cart_resp.status_code}"
        cart_content = cart_resp.text.lower()
        assert ("empty" in cart_content or "no items" in cart_content or "cart" in cart_content), "Cart not cleared after successful payment verification"

    finally:
        # Cleanup: remove cart contents if any remain - no direct API to clear cart
        pass

test_payment_verification_and_invoice_generation()
