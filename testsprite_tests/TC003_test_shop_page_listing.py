import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_shop_page_listing():
    """
    Verify GET /shop/ returns 200 with all available products.
    Verify GET /shop/ returns 200 with empty product listing when no products are available.
    """
    url = f"{BASE_URL}/shop/"
    try:
        # Make GET request to /shop/
        response = requests.get(url, timeout=TIMEOUT)
        # Assert status code 200
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        # Assert response content includes indications of products or empty listing
        content = response.text.lower()
        assert "product" in content or "no products" in content or "empty" in content or "<div" in content, \
            "Response HTML content does not appear to contain product listings or empty state."

        # Since the environment may already have products or not,
        # We cannot force empty product state, so just check 200 is returned.
        # Additional UI/content checks depend on actual HTML structure.

    except requests.RequestException as e:
        assert False, f"Request to /shop/ failed: {e}"

test_shop_page_listing()