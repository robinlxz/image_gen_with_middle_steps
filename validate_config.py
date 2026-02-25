import os
import requests
from dotenv import load_dotenv

def validate_config():
    """
    Validates the .env configuration by attempting to connect to configured endpoints.
    """
    print("🚀 Starting Configuration Validation...\n")
    
    # Load .env
    load_dotenv()
    
    # 1. Validate Image Generation Config
    print("🎨 Checking Image Generation Config (BytePlus)...")
    img_api_key = os.getenv("IMAGE_GEN_API_KEY")
    img_base_url = os.getenv("ARK_BASE_URL")
    
    if not img_api_key:
        print("❌ ERROR: IMAGE_GEN_API_KEY is missing!")
    elif not img_base_url:
        print("❌ ERROR: ARK_BASE_URL is missing!")
    else:
        # Test connection (using a list models endpoint or similar if available, or just auth check)
        # Note: BytePlus doesn't always have a simple 'whoami' endpoint, so we check if we get 401
        try:
            headers = {"Authorization": f"Bearer {img_api_key}"}
            # Try to list models (standard OpenAI endpoint)
            resp = requests.get(f"{img_base_url}/models", headers=headers, timeout=10)
            
            if resp.status_code == 200:
                print(f"✅ Success! Connected to Image API at {img_base_url}")
                models = resp.json().get('data', [])
                print(f"   -> Found {len(models)} models available.")
            elif resp.status_code == 401:
                print("❌ ERROR: Authentication Failed (401). Check your IMAGE_GEN_API_KEY.")
            else:
                print(f"⚠️ WARNING: Unexpected status {resp.status_code}. Response: {resp.text[:100]}")
        except Exception as e:
            print(f"❌ ERROR: Connection failed: {e}")

    print("-" * 30)

    # 2. Validate Text Generation Config
    print("📝 Checking Text Generation Config (BytePlus)...")
    text_api_key = os.getenv("TEXT_GEN_API_KEY")
    text_base_url = os.getenv("TEXT_GEN_BASE_URL")
    text_model = os.getenv("TEXT_GEN_MODEL_ENDPOINT")
    
    if not text_api_key:
        print("⚠️ SKIP: TEXT_GEN_API_KEY not set. Prompt enhancement will be disabled.")
    elif not text_base_url:
        print("❌ ERROR: TEXT_GEN_BASE_URL is missing!")
    elif "bytepluses.com" not in text_base_url:
         print(f"⚠️ WARNING: TEXT_GEN_BASE_URL ({text_base_url}) does not look like a BytePlus endpoint!")
    else:
        try:
            headers = {"Authorization": f"Bearer {text_api_key}"}
            # Test connection
            resp = requests.get(f"{text_base_url}/models", headers=headers, timeout=10)
            
            if resp.status_code == 200:
                print(f"✅ Success! Connected to Text API at {text_base_url}")
                # Verify if the specific model ID exists in the list (optional, might not be listed)
                if text_model:
                    print(f"   -> Configured Model ID: {text_model}")
            elif resp.status_code == 401:
                print("❌ ERROR: Authentication Failed (401). Check your TEXT_GEN_API_KEY.")
            else:
                print(f"⚠️ WARNING: Unexpected status {resp.status_code}. Response: {resp.text[:100]}")
        except Exception as e:
            print(f"❌ ERROR: Connection failed: {e}")

    print("\n🎉 Validation Complete.")

if __name__ == "__main__":
    validate_config()
