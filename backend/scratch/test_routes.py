
import requests

try:
    resp = requests.get("http://localhost:8000/health")
    print(f"Health: {resp.status_code}")
except Exception as e:
    print(f"Health check failed: {e}")

try:
    resp = requests.get("http://localhost:8000/auth/start", allow_redirects=False)
    print(f"Auth Start status: {resp.status_code}")
    print(f"Redirect Location: {resp.headers.get('Location')}")
except Exception as e:
    print(f"Auth Start check failed: {e}")

try:
    resp = requests.get("http://localhost:8000/login")
    print(f"Login page status: {resp.status_code}")
except Exception as e:
    print(f"Login page check failed: {e}")
