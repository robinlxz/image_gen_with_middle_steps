import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
API_KEY = os.getenv("IMAGE_GEN_API_KEY")
MODEL_ENDPOINT_ID = os.getenv("IMAGE_GEN_ENDPOINT")

# Initialize Ark Client
client = Ark(api_key=API_KEY)

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

@app.route('/generate', methods=['POST'])
def generate_image():
    if not API_KEY or not MODEL_ENDPOINT_ID:
        return jsonify({"error": "API Key or Endpoint ID not configured in .env"}), 500

    data = request.json
    user_prompt = data.get('prompt')
    
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Step 1: Process the prompt
    final_prompt = process_prompt(user_prompt)

    try:
        # Step 2: Call the Image Generation API via Ark SDK
        # Using the standard image generation method for Ark
        response = client.images.generate(
            model=MODEL_ENDPOINT_ID,
            prompt=final_prompt,
            size="1024x1024",  # Adjust if your model supports different sizes
            n=1
        )
        
        # Extract image URL
        if response.data and len(response.data) > 0:
            image_url = response.data[0].url
            return jsonify({
                "image_url": image_url, 
                "original_prompt": user_prompt,
                "final_prompt": final_prompt
            })
        else:
            return jsonify({"error": "No image data returned from API"}), 500

    except Exception as e:
        print(f"Error generating image: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
