import os
import requests
from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("IMAGE_GEN_API_KEY")

print("----- Diagnostic Report -----")
print(f"✅ API Key found: {api_key[:4]}...{api_key[-4:]} (Length: {len(api_key)})")

# 2. Test Volcengine (China) Endpoint
print("\n[Test 1] Volcengine (China) - https://ark.cn-beijing.volces.com/api/v3")
try:
    resp = requests.get(
        "https://ark.cn-beijing.volces.com/api/v3/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=5
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("✅ Success!")
    else:
        print(f"❌ Failed: {resp.json()}")
except Exception as e:
    print(f"❌ Connection Error: {e}")

# 3. Test BytePlus (International) Endpoint
print("\n[Test 2] BytePlus (International) - https://ark.byteplusapi.com/api/v3")
try:
    resp = requests.get(
        "https://ark.byteplusapi.com/api/v3/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=5
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("✅ Success! This is the correct endpoint.")
    else:
        print(f"❌ Failed: {resp.json()}")
except Exception as e:
    print(f"❌ Connection Error: {e}")

print("\n-----------------------------")
