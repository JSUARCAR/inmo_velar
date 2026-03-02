import requests
import sys

# Configuration
BASE_URL = "http://localhost:8000"
FILENAME = "contrato_mandato_17_20260206183311.pdf" # Using an existing file
DOWNLOAD_URL = f"{BASE_URL}/api/pdf/download/{FILENAME}"

def test_download():
    print(f"Testing download from: {DOWNLOAD_URL}")
    
    try:
        response = requests.get(DOWNLOAD_URL, stream=True)
        
        # 1. Check Status Code
        if response.status_code != 200:
            print(f"❌ Failed: Status code {response.status_code}")
            print(f"Response: {response.text}")
            sys.exit(1)
            
        print("✅ Status Code 200 OK")
        
        # 2. Check Headers
        content_type = response.headers.get("Content-Type")
        content_disposition = response.headers.get("Content-Disposition")
        content_length = response.headers.get("Content-Length")
        
        print(f"Content-Type: {content_type}")
        print(f"Content-Disposition: {content_disposition}")
        print(f"Content-Length: {content_length}")
        
        if content_type != "application/pdf":
            print("❌ Failed: Incorrect Content-Type")
            sys.exit(1)
            
        if "attachment" not in content_disposition or FILENAME not in content_disposition:
            print("❌ Failed: Incorrect Content-Disposition")
            sys.exit(1)
            
        if not content_length:
            print("⚠️ Warning: content-length missing")
            
        # 3. Check Content (Magic Bytes)
        # Read first 4 bytes
        magic_bytes = next(response.iter_content(4))
        if magic_bytes.startswith(b"%PDF"):
            print("✅ Magic Bytes Valid (%PDF)")
        else:
            print(f"❌ Failed: Invalid Magic Bytes: {magic_bytes}")
            sys.exit(1)
            
        print("\n🎉 Verification Successful! API is serving PDFs correctly.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Failed: Could not connect to server. Is it running?")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_download()
