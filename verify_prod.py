import requests
import json

urls = [
    "https://dz-kitab-backend.vercel.app/",
    "https://dz-kitab-backend.vercel.app/health",
    "https://dz-kitab-backend.vercel.app/auth/register"
]

for url in urls:
    print(f"\n--- TESTING: {url} ---")
    try:
        # Use a fake Origin to trigger CORS logic
        headers = {"Origin": "https://dz-kitab-frontend.vercel.app"}
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        print("Headers:")
        for k, v in r.headers.items():
            if "access-control" in k.lower() or "vercel" in k.lower():
                print(f"  {k}: {v}")
        
        try:
            print(f"Body (JSON): {json.dumps(r.json(), indent=2)}")
        except:
            print(f"Body (Text): {r.text[:500]}...")
            
    except Exception as e:
        print(f"Request Error: {e}")

# Test Preflight
print("\n--- TESTING PREFLIGHT (OPTIONS) ---")
url_pre = "https://dz-kitab-backend.vercel.app/auth/register"
headers_pre = {
    "Origin": "https://dz-kitab-frontend.vercel.app",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type"
}
try:
    r = requests.options(url_pre, headers=headers_pre, timeout=10)
    print(f"Status: {r.status_code}")
    print("Headers:")
    for k, v in r.headers.items():
        if "access-control" in k.lower():
            print(f"  {k}: {v}")
except Exception as e:
    print(f"Preflight Error: {e}")
