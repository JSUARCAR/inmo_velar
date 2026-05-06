import requests
import sys

url = "http://localhost:8000/api/pdf/download/contrato_mandato_17_20260206183311.pdf"

try:
    print(f"Testing URL: {url}")
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print("Headers:")
    for k, v in response.headers.items():
        print(f"  {k}: {v}")
    
    content_len = len(response.content)
    print(f"Content Length (received): {content_len}")
    
    if content_len > 10:
        print(f"First 10 bytes: {response.content[:10]}")
    else:
        print(f"Content: {response.content}")
        
    expected_len = 39272 # From list_dir
    print(f"Expected Length (approx): {expected_len}")
    
except Exception as e:
    print(f"Error: {e}")
