import os, requests

BASE = os.getenv("BASE_URL") or "http://localhost:8000"

payload = {
  "topic": "Daily ChatRefill offer",
  "style": "clean, brand green, product marketing",
  "lang": "ht",
  "time": os.getenv("DEFAULT_POST_TIME","09:00"),
  "publish_now": False
}

r = requests.post(f"{BASE}/api/pipeline/generate-and-schedule",
                  json=payload, timeout=300)

print("Status:", r.status_code)
try:
    print("Response:", r.json())
except Exception:
    print("Text:", r.text)
