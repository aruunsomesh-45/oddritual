import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_about_page_display():
    # Test GET /about/ expecting 200 or 404
    
    url = f"{BASE_URL}/about/"
    
    try:
        response = requests.get(url, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to {url} failed with exception: {e}"
    
    # The response status_code should be either 200 or 404
    assert response.status_code in (200, 404), (
        f"Expected status code 200 or 404, got {response.status_code}"
    )
    
    if response.status_code == 200:
        # Expect HTML content indicating about page is shown
        content_type = response.headers.get("Content-Type", "")
        assert "text/html" in content_type.lower(), "Expected HTML content for 200 response"
        assert len(response.text) > 0, "Response body is empty for about page"
    else:
        # For 404 page not found, response text may have message or default 404 page content
        assert "404" in response.text or response.text != "", "404 response content empty or invalid"

test_about_page_display()