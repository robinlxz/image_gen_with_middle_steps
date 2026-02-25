import requests
import sys

# Try to connect to the running Flask server
try:
    print("Testing static file serving...")
    # 1. Request the CSS file
    url = "http://127.0.0.1:5000/static/style.css"
    print(f"GET {url}")
    
    response = requests.get(url, timeout=5)
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content Length: {len(response.text)} bytes")
    
    # 2. Analyze the content
    content_preview = response.text[:100].replace('\n', '\\n')
    print(f"Content Preview: {content_preview}...")
    
    if response.status_code == 200:
        if "text/css" in response.headers.get('Content-Type', ''):
            print("✅ SUCCESS: Server is returning CSS correctly.")
        else:
            print("❌ ERROR: Server returned 200 but wrong Content-Type.")
            if "<!DOCTYPE html>" in response.text:
                print("   -> It seems to be returning an HTML page instead of CSS. Check your routes.")
    elif response.status_code == 404:
        print("❌ ERROR: 404 Not Found. Flask cannot find the file in the 'static' folder.")
    else:
        print(f"❌ ERROR: Unexpected status code {response.status_code}")

except requests.exceptions.ConnectionError:
    print("❌ ERROR: Could not connect to http://127.0.0.1:5000. Is the server running?")
except Exception as e:
    print(f"❌ ERROR: {e}")
