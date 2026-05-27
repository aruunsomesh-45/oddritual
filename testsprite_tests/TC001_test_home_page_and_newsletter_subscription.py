import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def test_home_page_and_newsletter_subscription():
    session = requests.Session()

    # 1. Verify GET / returns 200 with home page content including products and community highlights
    try:
        response_get = session.get(f"{BASE_URL}/", timeout=TIMEOUT, headers=HEADERS)
        assert response_get.status_code == 200, f"Expected status 200 but got {response_get.status_code}"
        content = response_get.text.lower()
        # Basic checks for 'products' and 'community' keywords in content (as homepage should include these)
        assert "product" in content, "Home page content does not include product highlights"
        assert "community" in content, "Home page content does not include community highlights"
    except (requests.RequestException, AssertionError) as e:
        raise AssertionError(f"GET / failed: {e}")

    # 2. Verify POST / with valid name and email subscribes to newsletter and redirects with 302
    valid_data = {
        "name": "Test User",
        "email": "testuser@example.com"
    }
    headers_post = HEADERS.copy()
    # Set Content-Type for form submission
    headers_post["Content-Type"] = "application/x-www-form-urlencoded"
    try:
        response_post_valid = session.post(f"{BASE_URL}/", data=valid_data, headers=headers_post, timeout=TIMEOUT, allow_redirects=False)
        assert response_post_valid.status_code == 302, f"Expected 302 redirect on valid subscription, got {response_post_valid.status_code}"
        location = response_post_valid.headers.get("Location", "")
        # The redirect should be back to the home page "/"
        assert location == "/" or location == f"{BASE_URL}/", f"Expected redirect to '/', got {location}"
    except (requests.RequestException, AssertionError) as e:
        raise AssertionError(f"POST / with valid data failed: {e}")

    # 3. Verify POST / with missing or invalid fields returns form error and remains on home page
    # Missing email
    invalid_data_missing_email = {
        "name": "Test User"
    }
    # Missing name
    invalid_data_missing_name = {
        "email": "testuser@example.com"
    }
    # Invalid email (empty string)
    invalid_data_invalid_email = {
        "name": "Test User",
        "email": ""
    }

    invalid_test_cases = [
        invalid_data_missing_email,
        invalid_data_missing_name,
        invalid_data_invalid_email,
    ]

    for idx, invalid_data in enumerate(invalid_test_cases, start=1):
        try:
            response_post_invalid = session.post(f"{BASE_URL}/", data=invalid_data, headers=headers_post, timeout=TIMEOUT, allow_redirects=True)
            # Should return 200 and remain on home page (form error)
            assert response_post_invalid.status_code == 200, f"Invalid data case {idx}: Expected status 200 to remain on home page, got {response_post_invalid.status_code}"
            # The response should include some error indication; we cannot parse exact error without schema,
            # but ensure form fields are present as indicator of remaining on home page.
            content = response_post_invalid.text.lower()
            assert "name" in content and "email" in content, f"Invalid data case {idx}: Home page form fields missing on error display"
            # Also check that it does not redirect (no 3xx)
            assert not (300 <= response_post_invalid.status_code < 400), f"Invalid data case {idx}: Unexpected redirect on invalid submission"
        except (requests.RequestException, AssertionError) as e:
            raise AssertionError(f"POST / with invalid data case {idx} failed: {e}")


test_home_page_and_newsletter_subscription()