
import requests
import os

def verify_download():
    # URL with the new query parameter
    url = "http://localhost:8000/api/storage/17/download?force_download=true"
    print(f"Testing forced download from: {url}")
    
    try:
        response = requests.get(url, stream=True)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        
        if response.status_code == 200:
            content_length = len(response.content)
            print(f"Content Length: {content_length} bytes")
            
            # Verify Content-Disposition header
            disposition = response.headers.get("content-disposition", "")
            if "attachment" in disposition:
                print("✅ SUCCESS: Content-Disposition contains 'attachment'.")
            else:
                print(f"❌ WARNING: Content-Disposition is '{disposition}', expected 'attachment'.")

            if content_length > 0:
                filename = "test_download_forced_17.png"
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"✅ SUCCESS: File saved as {filename}")
            else:
                print("❌ ERROR: Content is empty (0 bytes).")
        else:
            print(f"❌ ERROR: Failed with status code {response.status_code}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    verify_download()
