import requests
import json
try:
    r = requests.get('https://dz-backend-fix.vercel.app/health')
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
