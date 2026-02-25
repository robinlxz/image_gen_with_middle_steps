import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
API_KEY = os.getenv("IMAGE_GEN_API_KEY")
BASE_URL = os.getenv("ARK_BASE_URL", "https://ark.ap-southeast.bytepluses.com/api/v3")

# Define available models
MODELS = {
    "model_1": {
        "name": os.getenv("MODEL_1_NAME", "Seedream 5.0 Lite"),
        "endpoint": os.getenv("MODEL_1_ENDPOINT"),
        "size": os.getenv("MODEL_1_SIZE", "1920x1920")
    },
    "model_2": {
        "name": os.getenv("MODEL_2_NAME", "Seedream 4.0"),
        "endpoint": os.getenv("MODEL_2_ENDPOINT"),
        "size": os.getenv("MODEL_2_SIZE", "1024x1024")
    }
}

# Initialize OpenAI Client
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

def process_prompt(original_prompt):
    """
    Placeholder for future AI Agent steps.
    Currently just returns the prompt as-is.
    """
    print(f"Original Prompt: {original_prompt}")
    refined_prompt = original_prompt 
    print(f"Processed Prompt: {refined_prompt}")
    return refined_prompt

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/config', methods=['GET'])
def get_config():
    """Return available models to frontend"""
    return jsonify({
        "models": [
            {"id": "model_1", "name": MODELS["model_1"]["name"]},
            {"id": "model_2", "name": MODELS["model_2"]["name"]}
        ]
    })

@app.route('/generate', methods=['POST'])
def generate_image():
    if not API_KEY:
        return jsonify({"error": "API Key not configured in .env"}), 500

    data = request.json
    user_prompt = data.get('prompt')
    model_id = data.get('model_id', 'model_2') # Default to model_2 (cheaper one)
    
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Get model configuration
    selected_model = MODELS.get(model_id)
    if not selected_model or not selected_model["endpoint"]:
        return jsonify({"error": "Invalid model selected or model not configured"}), 400

    # Step 1: Process the prompt
    final_prompt = process_prompt(user_prompt)

    try:
        print(f"Generating with Model: {selected_model['name']} ({selected_model['endpoint']})")
        print(f"Size: {selected_model['size']}")

        # Step 2: Call the Image Generation API via OpenAI SDK
        response = client.images.generate(
            model=selected_model["endpoint"],
            prompt=final_prompt,
            size=selected_model["size"], 
        )
        
        # Extract image URL
        if response.data and len(response.data) > 0:
            image_url = response.data[0].url
            return jsonify({
                "image_url": image_url, 
                "original_prompt": user_prompt,
                "final_prompt": final_prompt,
                "model_used": selected_model["name"]
            })
        else:
            return jsonify({"error": "No image data returned from API"}), 500

    except Exception as e:
        print(f"Error generating image: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
