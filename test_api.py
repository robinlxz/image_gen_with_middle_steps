import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

API_KEY = os.getenv("IMAGE_GEN_API_KEY")
BASE_URL = os.getenv("ARK_BASE_URL")
ACCESS_CODE = os.getenv("ACCESS_CODE")

def test_image_generation():
    print("\n🎨 Testing Image Generation API...")
    if not API_KEY:
        print("❌ Error: IMAGE_GEN_API_KEY not found in .env")
        return

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    # Use Model 2 (Seedream 4.0) for testing as it's usually faster/cheaper
    model_endpoint = os.getenv("MODEL_2_ENDPOINT")
    
    if not model_endpoint:
        print("⚠️ Warning: MODEL_2_ENDPOINT not found, skipping generation test.")
        return

    try:
        print(f"   Using Endpoint: {model_endpoint}")
        response = client.images.generate(
            model=model_endpoint,
            prompt="A simple test image of a geometric cube, white background",
            size="1024x1024"
        )
        
        if response.data:
            print(f"✅ Success! Image URL: {response.data[0].url}")
        else:
            print("❌ Failed: No data returned.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_text_generation():
    print("\n📝 Testing Text Generation API (Prompt Enhancement)...")
    text_key = os.getenv("TEXT_GEN_API_KEY")
    text_url = os.getenv("TEXT_GEN_BASE_URL")
    text_model = os.getenv("TEXT_GEN_MODEL_ENDPOINT")

    if not text_key or not text_model:
        print("⚠️ Text generation config missing, skipping test.")
        return

    client = OpenAI(api_key=text_key, base_url=text_url)

    try:
        response = client.chat.completions.create(
            model=text_model,
            messages=[
                {"role": "system", "content": "You are a helper."},
                {"role": "user", "content": "Say 'Hello World'"}
            ]
        )
        print(f"✅ Success! Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_local_auth():
    print("\n🔐 Testing Local Server Auth...")
    # This assumes the Flask server is running locally on port 5000
    # If not running, this test will fail gracefully
    url = "http://127.0.0.1:5000/generate"
    
    try:
        # 1. Test without Access Code
        resp = requests.post(url, json={"prompt": "test"})
        if resp.status_code == 401:
            print("✅ Success: Server rejected request without Access Code (401).")
        elif resp.status_code == 500 or resp.status_code == 200:
             print(f"⚠️ Warning: Server returned {resp.status_code}. Is ACCESS_CODE set?")
        else:
             print(f"ℹ️ Server unreachable or error: {resp.status_code} (Is it running?)")

        # 2. Test with Access Code (if configured)
        if ACCESS_CODE:
            resp = requests.post(url, json={"prompt": "test", "access_code": ACCESS_CODE})
            if resp.status_code == 200 or resp.status_code == 400: # 400 is fine (missing model_id etc), just passed auth
                print("✅ Success: Server accepted request with correct Access Code.")
            elif resp.status_code == 401:
                print("❌ Failed: Server rejected correct Access Code.")
                
    except requests.exceptions.ConnectionError:
        print("⚠️ Skipped: Local server is not running at http://127.0.0.1:5000")

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Tests...")
    test_image_generation()
    test_text_generation()
    test_local_auth()
