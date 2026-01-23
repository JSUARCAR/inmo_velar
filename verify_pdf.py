import requests
try:
    url = "http://localhost:8000/api/pdf/download/contrato_5_20260119164706.pdf"
    print(f"Testing URL: {url}")
    r = requests.get(url)
    print(f"Status Code: {r.status_code}")
    print(f"Content-Disposition: {r.headers.get('Content-Disposition')}")
except Exception as e:
    print(f"Error: {e}")
