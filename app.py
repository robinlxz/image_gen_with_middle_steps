import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Ensure Flask knows where static files are
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Configuration
API_KEY = os.getenv("IMAGE_GEN_API_KEY")
BASE_URL = os.getenv("ARK_BASE_URL", "https://ark.ap-southeast.bytepluses.com/api/v3")

# Text Generation Config
TEXT_API_KEY = os.getenv("TEXT_GEN_API_KEY")
TEXT_BASE_URL = os.getenv("TEXT_GEN_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
TEXT_MODEL_ENDPOINT = os.getenv("TEXT_GEN_MODEL_ENDPOINT")

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

# Define Style Presets
STYLES = {
    "none": {
        "name": "Default",
        "prompt_suffix": ""
    },
    "cyberpunk": {
        "name": "Cyberpunk",
        "prompt_suffix": ", cyberpunk style, neon lights, futuristic city background, highly detailed, 8k resolution, vibrant colors"
    },
    "watercolor": {
        "name": "Watercolor",
        "prompt_suffix": ", watercolor painting, soft colors, artistic, dreamy, paper texture, delicate brush strokes"
    },
    "ghibli": {
        "name": "Ghibli Anime",
        "prompt_suffix": ", Studio Ghibli style, anime, vibrant colors, detailed background, whimsical, Hayao Miyazaki"
    },
    "3d_render": {
        "name": "3D Render",
        "prompt_suffix": ", 3D render, unreal engine 5, 8k, ray tracing, realistic, cinematic lighting, highly detailed textures"
    },
    "oil_painting": {
        "name": "Oil Painting",
        "prompt_suffix": ", oil painting, thick brush strokes, textured canvas, classical art style, rich colors"
    }
}

# Initialize OpenAI Client (Image)
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# Initialize OpenAI Client (Text - Optional)
text_client = None
if TEXT_API_KEY and TEXT_MODEL_ENDPOINT:
    text_client = OpenAI(
        api_key=TEXT_API_KEY,
        base_url=TEXT_BASE_URL
    )

def enhance_prompt(user_prompt, style_suffix):
    """
    Use LLM to rewrite and enhance the prompt.
    """
    if not text_client:
        return f"{user_prompt}{style_suffix}"

    try:
        system_prompt = """
        You are an expert AI art prompt generator. 
        Your task is to take a user's basic description and a style, and rewrite it into a detailed, high-quality prompt for image generation.
        
        Rules:
        1. Keep the prompt in English.
        2. Focus on visual details, lighting, texture, and composition.
        3. Incorporate the requested style naturally.
        4. Output ONLY the final prompt text, no explanations.
        """
        
        user_message = f"Description: {user_prompt}\nStyle/Suffix to incorporate: {style_suffix}"
        
        response = text_client.chat.completions.create(
            model=TEXT_MODEL_ENDPOINT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
        )
        
        enhanced_prompt = response.choices[0].message.content.strip()
        print(f"Enhanced Prompt: {enhanced_prompt}")
        return enhanced_prompt
        
    except Exception as e:
        print(f"Prompt enhancement failed: {e}")
        # Fallback to simple concatenation
        return f"{user_prompt}{style_suffix}"

def process_prompt(original_prompt, style_id="none"):
    """
    Process the user prompt by appending the selected style suffix or using LLM enhancement.
    """
    print(f"Original Prompt: {original_prompt}")
    
    style = STYLES.get(style_id)
    style_suffix = style['prompt_suffix'] if style else ""
    style_name = style['name'] if style else "Default"
    
    # If LLM is configured, use it to enhance the prompt
    if text_client:
        print(f"Enhancing prompt with style: {style_name}")
        refined_prompt = enhance_prompt(original_prompt, style_suffix)
    else:
        # Fallback to simple concatenation
        if style:
            refined_prompt = f"{original_prompt}{style_suffix}"
            print(f"Applied Style: {style_name}")
        else:
            refined_prompt = original_prompt
            print("No style applied")
        
    print(f"Processed Prompt: {refined_prompt}")
    return refined_prompt

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/config', methods=['GET'])
def get_config():
    """Return available models and styles to frontend"""
    return jsonify({
        "models": [
            {"id": "model_1", "name": MODELS["model_1"]["name"]},
            {"id": "model_2", "name": MODELS["model_2"]["name"]}
        ],
        "styles": [
            {"id": k, "name": v["name"]} for k, v in STYLES.items()
        ]
    })

@app.route('/generate', methods=['POST'])
def generate_image():
    if not API_KEY:
        return jsonify({"error": "API Key not configured in .env"}), 500

    data = request.json
    user_prompt = data.get('prompt')
    model_id = data.get('model_id', 'model_2') # Default to model_2 (cheaper one)
    style_id = data.get('style_id', 'none')
    
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Get model configuration
    selected_model = MODELS.get(model_id)
    if not selected_model or not selected_model["endpoint"]:
        return jsonify({"error": "Invalid model selected or model not configured"}), 400

    # Step 1: Process the prompt (Apply Style)
    final_prompt = process_prompt(user_prompt, style_id)

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
            
            # Get style name for response
            style_name = STYLES.get(style_id, {}).get("name", "Unknown")
            
            return jsonify({
                "image_url": image_url, 
                "original_prompt": user_prompt,
                "final_prompt": final_prompt,
                "model_used": selected_model["name"],
                "style_used": style_name
            })
        else:
            return jsonify({"error": "No image data returned from API"}), 500

    except Exception as e:
        print(f"Error generating image: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
