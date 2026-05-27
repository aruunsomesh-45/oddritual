import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Replace these with valid staff credentials for the test environment
STAFF_USERNAME = "admin"
STAFF_PASSWORD = "adminpassword"


def test_django_admin_access_control():
    admin_url = f"{BASE_URL}/admin/"

    # Test 1: GET /admin/ with valid authenticated staff credentials should return 200 and contain admin HTML page content
    try:
        auth_response = requests.get(admin_url, auth=HTTPBasicAuth(STAFF_USERNAME, STAFF_PASSWORD), timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Authenticated request to /admin/ failed with exception: {e}"

    assert auth_response.status_code == 200, f"Expected status code 200 for authenticated admin access, got {auth_response.status_code}"
    content_type = auth_response.headers.get("Content-Type", "")
    # Check content type is probably HTML
    assert "text/html" in content_type, f"Expected 'text/html' in Content-Type header, got {content_type}"
    # Check for admin HTML elements in the response content as a heuristic (e.g. 'Django administration' title)
    assert (
        "Django administration" in auth_response.text or "<title>Site administration</title>" in auth_response.text
    ), "Admin page content missing expected text."

    # Test 2: GET /admin/ without authentication should be denied or redirect to login
    try:
        noauth_response = requests.get(admin_url, allow_redirects=False, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Unauthenticated request to /admin/ failed with exception: {e}"

    # Expected: 302 redirection to login page or 401/403 response denying access
    assert noauth_response.status_code in (302, 401, 403), (
        f"Expected status code 302 or 401 or 403 for unauthenticated admin access, got {noauth_response.status_code}"
    )
    if noauth_response.status_code == 302:
        location = noauth_response.headers.get("Location", "")
        # The redirect location should point to a login page URL containing 'login'
        assert "login" in location.lower(), f"Expected redirect location to include 'login', got: {location}"
    else:
        # For 401 or 403, check for expected keywords in the response body (optional)
        assert any(
            keyword in noauth_response.text.lower() for keyword in ["login", "forbidden", "unauthorized", "authentication"]
        ), "Expected login or access denied message in response body."


test_django_admin_access_control()