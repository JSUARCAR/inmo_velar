
import requests
import sys

# Configuration
BASE_URL = "http://localhost:8000"
FILENAME = "contrato_mandato_70_20260302175348.pdf" # Using an existing file
DOWNLOAD_URL = f"{BASE_URL}/api/pdf/download/{FILENAME}"

def test_download():
    print(f"Testing download from: {DOWNLOAD_URL}")
    
    try:
        response = requests.get(DOWNLOAD_URL, stream=True)
        
        # 1. Check Status Code
        if response.status_code != 200:
            print(f"x Failed: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return
            
        print("v Status Code 200 OK")
        
        # 2. Check Headers
        content_type = response.headers.get("Content-Type")
        content_disposition = response.headers.get("Content-Disposition")
        content_length = response.headers.get("Content-Length")
        
        print(f"Content-Type: {content_type}")
        print(f"Content-Disposition: {content_disposition}")
        print(f"Content-Length: {content_length}")
        
        # 3. Check Content (Magic Bytes)
        # Read first 4 bytes
        magic_bytes = next(response.iter_content(4))
        if magic_bytes.startswith(b"%PDF"):
            print("v Magic Bytes Valid (%PDF)")
        else:
            print(f"x Failed: Invalid Magic Bytes: {magic_bytes}")
            
    except Exception as e:
        print(f"x An error occurred: {e}")

if __name__ == "__main__":
    test_download()
