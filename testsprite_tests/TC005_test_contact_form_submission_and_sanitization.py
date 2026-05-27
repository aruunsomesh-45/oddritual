import requests
from urllib.parse import urljoin
import re

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def get_csrf_token(session, url):
    try:
        resp = session.get(url, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"GET request to {url} failed: {e}"
    
    # Try to extract csrfmiddlewaretoken value from form
    match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\'](.*?)["\']', resp.text)
    if not match:
        # Try alternate pattern (common in Django forms)
        match = re.search(r'csrfmiddlewaretoken" value="(.*?)"', resp.text)
    if not match:
        assert False, "CSRF token not found in the page"
    return match.group(1)

def test_contact_form_submission_and_sanitization():
    session = requests.Session()
    contact_url = urljoin(BASE_URL, "/contact/")
    
    # 1. Verify GET /contact/ returns 200 with contact form page
    try:
        get_resp = session.get(contact_url, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"GET /contact/ request failed: {e}"
    assert get_resp.status_code == 200, f"Expected 200 OK, got {get_resp.status_code}"
    assert "form" in get_resp.text.lower(), "Response does not contain a form"
    
    # Fetch CSRF token
    csrf_token = get_csrf_token(session, contact_url)
    
    # 2. POST /contact/ with valid name, email, and message -> 302 redirect with success message
    valid_data = {
        "name": "Test User",
        "email": "test.user@example.com",
        "message": "This is a valid contact message.",
        "csrfmiddlewaretoken": csrf_token
    }
    try:
        post_resp_valid = session.post(contact_url, data=valid_data, allow_redirects=False, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"POST /contact/ with valid data failed: {e}"
    assert post_resp_valid.status_code == 302, f"Expected 302 redirect, got {post_resp_valid.status_code}"
    location = post_resp_valid.headers.get("Location", "")
    assert location.endswith("/contact/"), f"Expected redirect to /contact/, got {location}"
    
    # Follow the redirect to verify success message on redirected page
    try:
        redirect_resp = session.get(urljoin(BASE_URL, location), timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"GET after redirect failed: {e}"
    assert redirect_resp.status_code == 200, "Redirected page did not return 200 OK"
    assert ("success" in redirect_resp.text.lower()) or ("thank you" in redirect_resp.text.lower()), "Success message not found on redirected page"
    
    # 3. POST /contact/ with invalid or incomplete fields -> 302 redirect with error message
    invalid_data_list = [
        {"name": "", "email": "test.user@example.com", "message": "Valid message"},
        {"name": "Test User", "email": "", "message": "Valid message"},
        {"name": "Test User", "email": "invalid-email", "message": "Valid message"},
        {"name": "Test User", "email": "test.user@example.com", "message": ""}
    ]
    for invalid_data in invalid_data_list:
        # refresh csrf token for each post
        csrf_token_invalid = get_csrf_token(session, contact_url)
        invalid_data["csrfmiddlewaretoken"] = csrf_token_invalid
        try:
            post_resp_invalid = session.post(contact_url, data=invalid_data, allow_redirects=False, timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"POST /contact/ with invalid data {invalid_data} failed: {e}"
        assert post_resp_invalid.status_code == 302, f"Expected 302 redirect for invalid data {invalid_data}, got {post_resp_invalid.status_code}"
        loc_invalid = post_resp_invalid.headers.get("Location", "")
        assert loc_invalid.endswith("/contact/"), f"Expected redirect to /contact/ for invalid data, got {loc_invalid}"
        # Fetch redirected page to check for error message
        try:
            err_page = session.get(urljoin(BASE_URL, loc_invalid), timeout=TIMEOUT)
        except requests.RequestException as e:
            assert False, f"GET after invalid redirect failed: {e}"
        assert err_page.status_code == 200, f"Redirected page for invalid data did not return 200 OK"
        content_lower = err_page.text.lower()
        assert ("error" in content_lower) or ("required" in content_lower) or ("invalid" in content_lower), f"Error message not found for invalid data {invalid_data}"
    
    # 4. POST /contact/ with HTML content in message is sanitized before processing
    html_message = "<script>alert('xss')</script>Thank you for your product."
    post_data_html = {
        "name": "User HTML",
        "email": "html.user@example.com",
        "message": html_message,
        "csrfmiddlewaretoken": get_csrf_token(session, contact_url)
    }
    try:
        post_resp_html = session.post(contact_url, data=post_data_html, allow_redirects=False, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"POST /contact/ with HTML content failed: {e}"
    assert post_resp_html.status_code == 302, f"Expected 302 redirect for HTML content, got {post_resp_html.status_code}"
    location_html = post_resp_html.headers.get("Location", "")
    assert location_html.endswith("/contact/"), f"Expected redirect to /contact/ after HTML content post, got {location_html}"

    # After redirect, get page to confirm success message (assumed sanitized)
    try:
        redirect_html_resp = session.get(urljoin(BASE_URL, location_html), timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"GET after redirect (HTML content) failed: {e}"
    assert redirect_html_resp.status_code == 200, "Redirected page after HTML content post did not return 200 OK"
    
    # Verify that raw HTML tags are not present in redirected page text (sanitization)
    # We expect the message to be sanitized and not contain raw <script> tags
    assert "<script>" not in redirect_html_resp.text.lower(), "Raw HTML tags found in the response, sanitization failed"
    assert "alert" not in redirect_html_resp.text.lower(), "Potential XSS script content found, sanitization failed"

test_contact_form_submission_and_sanitization()
