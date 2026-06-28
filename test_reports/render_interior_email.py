"""Fetch the interior email HTML from the backend, save to disk."""
import os
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001").rstrip("/")
CUSTOMER_ID = "6d902613-5106-4294-bc3e-b907f85127f7"

r = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": "crm@rrlbuildersanddevelopers.com",
    "password": "#RRLnew2026",
}, timeout=20)
r.raise_for_status()
token = r.json().get("access_token") or r.json().get("token")

resp = requests.get(
    f"{BASE_URL}/api/communication/preview-interior-email/{CUSTOMER_ID}",
    headers={"Authorization": f"Bearer {token}"},
    timeout=20,
)
resp.raise_for_status()
html = resp.json().get("email_html")
with open("/tmp/interior_email.html", "w") as f:
    f.write(html)
print(f"Saved {len(html)} chars to /tmp/interior_email.html")
