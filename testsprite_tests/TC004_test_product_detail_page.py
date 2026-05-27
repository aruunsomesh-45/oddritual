import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_product_detail_page():
    # Step 1: Retrieve product list from /shop/ to get a valid product ID
    try:
        resp_shop = requests.get(f"{BASE_URL}/shop/", timeout=TIMEOUT)
        assert resp_shop.status_code == 200, f"Expected 200 from /shop/, got {resp_shop.status_code}"
        content_shop = resp_shop.text
        
        import re
        # Attempt to extract a product ID from the shop page HTML
        # Assuming product detail links follow pattern /p/{pid}/ (called in href)
        product_ids = set(re.findall(r'href="/p/([^/]+)/"', content_shop))
        # If no product ids found, fallback to None - test will skip valid id test
        valid_pid = next(iter(product_ids), None)
    except Exception as e:
        raise AssertionError(f"Failed to get or parse /shop/ page for product IDs: {e}")

    # If valid_pid is available, test GET /p/{pid}/ returns 200 with product details
    if valid_pid:
        try:
            resp_valid = requests.get(f"{BASE_URL}/p/{valid_pid}/", timeout=TIMEOUT)
            assert resp_valid.status_code == 200, f"Expected 200 for valid product ID {valid_pid}, got {resp_valid.status_code}"
            assert "product" in resp_valid.text.lower() or "description" in resp_valid.text.lower(), "Response does not contain expected product details keywords"
        except Exception as e:
            raise AssertionError(f"GET /p/{valid_pid}/ failed or response invalid: {e}")
    else:
        print("Warning: No valid product ID found on /shop/, skipping valid product ID test.")

    # Step 2: Test GET /p/{non_existent_pid}/ returns 404 Product not found
    non_existent_pid = "nonexistent-product-id-1234567890"
    try:
        resp_404 = requests.get(f"{BASE_URL}/p/{non_existent_pid}/", timeout=TIMEOUT)
        assert resp_404.status_code == 404, f"Expected 404 for nonexistent product ID, got {resp_404.status_code}"
        assert "product not found" in resp_404.text.lower() or "not found" in resp_404.text.lower(), "404 response does not contain 'Product not found' message"
    except Exception as e:
        raise AssertionError(f"GET /p/{non_existent_pid}/ failed or response invalid: {e}")

test_product_detail_page()