import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_razorpay_order_creation():
    session = requests.Session()
    headers = {"Content-Type": "application/json"}

    def get_csrf_token():
        # Get CSRF token from cookie or from a page
        url = f"{BASE_URL}/shop/"
        r = session.get(url, timeout=TIMEOUT)
        if 'csrftoken' in session.cookies:
            return session.cookies['csrftoken']
        import re
        match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\'](.+?)["\']', r.text)
        if match:
            return match.group(1)
        return ''

    csrf_token = get_csrf_token()

    def add_product_to_cart(pid, size="M", quantity=1):
        add_url = f"{BASE_URL}/cart/add/{pid}/"
        data = {"size": size, "quantity": quantity, "csrfmiddlewaretoken": csrf_token}
        post_headers = {"Content-Type": "application/x-www-form-urlencoded", "Referer": add_url}
        return session.post(add_url, data=data, headers=post_headers, allow_redirects=False, timeout=TIMEOUT)

    def get_cart_page():
        return session.get(f"{BASE_URL}/cart/", timeout=TIMEOUT)

    def remove_cart_item(item_id):
        return session.get(f"{BASE_URL}/cart/remove/{item_id}/", allow_redirects=False, timeout=TIMEOUT)

    def create_order(payload=None):
        url = f"{BASE_URL}/payments/create-order/"
        json_payload = payload if payload is not None else {}
        return session.post(url, json=json_payload, headers=headers, timeout=TIMEOUT)

    shop_url = f"{BASE_URL}/shop/"
    r = session.get(shop_url, timeout=TIMEOUT)
    assert r.status_code == 200
    import re
    product_ids = re.findall(r'/p/([^/]+)/', r.text)
    assert product_ids, "No products found on /shop/ to use in test."

    valid_pid = product_ids[0]

    add_resp = add_product_to_cart(valid_pid)
    assert add_resp.status_code == 302, f"Add to cart redirect expected, got {add_resp.status_code}"

    cart_resp = get_cart_page()
    assert cart_resp.status_code == 200
    assert valid_pid in cart_resp.text, "Product ID should appear in cart page HTML"

    create_order_resp = create_order()
    assert create_order_resp.status_code == 200, f"Expected 200 for order creation with cart, got {create_order_resp.status_code}"
    order_json = create_order_resp.json()
    for key in ["order_id", "amount", "currency", "key_id"]:
        assert key in order_json, f"{key} missing in order creation response JSON"

    cart_page = get_cart_page()
    item_ids = re.findall(r'/cart/remove/(\w+)/', cart_page.text)
    for item_id in item_ids:
        rem_resp = remove_cart_item(item_id)
        assert rem_resp.status_code == 302, f"Expected 302 redirect on removing cart item, got {rem_resp.status_code}"

    empty_cart_page = get_cart_page()
    assert empty_cart_page.status_code == 200
    assert not re.search(r'/cart/remove/(\w+)/', empty_cart_page.text), "Cart should be empty after removals"

    fallback_resp = create_order({"product_id": valid_pid})
    assert fallback_resp.status_code == 200, f"Expected 200 for order creation fallback product_id, got {fallback_resp.status_code}"
    fallback_json = fallback_resp.json()
    for key in ["order_id", "amount", "currency", "key_id"]:
        assert key in fallback_json, f"{key} missing in fallback order creation response JSON"

    invalid_pid = "nonexistent12345"
    invalid_resp = create_order({"product_id": invalid_pid})
    assert invalid_resp.status_code == 404, f"Expected 404 for invalid product_id, got {invalid_resp.status_code}"

    malformed_url = f"{BASE_URL}/payments/create-order/"
    malformed_headers = {"Content-Type": "application/json"}
    malformed_data = "{invalid-json"
    mal_resp = session.post(malformed_url, data=malformed_data, headers=malformed_headers, timeout=TIMEOUT)
    assert mal_resp.status_code == 400, f"Expected 400 for malformed request data, got {mal_resp.status_code}"

test_razorpay_order_creation()
