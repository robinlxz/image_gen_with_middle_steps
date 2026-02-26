import os
import time
from datetime import datetime, date
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
ACCESS_CODE = os.getenv("ACCESS_CODE")  # Optional access code

# Rate Limiting Config
MAX_PROMPT_LENGTH = 1000

# Quotas per model ID
MODEL_QUOTAS = {
    "model_1": 50,   # Seedream 5.0 (Expensive)
    "model_2": 200   # Seedream 4.0 (Cheap)
}

# Simple In-Memory Rate Limiter
rate_limit_store = {
    "date": date.today(),
    "counts": {
        "model_1": 0,
        "model_2": 0
    }
}

def check_rate_limit(model_id):
    """Check if daily limit is exceeded for a specific model"""
    today = date.today()
    
    # Reset counter if new day
    if rate_limit_store["date"] != today:
        rate_limit_store["date"] = today
        rate_limit_store["counts"] = {k: 0 for k in MODEL_QUOTAS.keys()}
        
    current_count = rate_limit_store["counts"].get(model_id, 0)
    max_limit = MODEL_QUOTAS.get(model_id, 0)
    
    if current_count >= max_limit:
        return False, f"Daily limit of {max_limit} images reached for this model. Try the other model!"
        
    return True, ""

def increment_rate_limit(model_id):
    """Increment the daily counter for a specific model"""
    if model_id in rate_limit_store["counts"]:
        rate_limit_store["counts"][model_id] += 1
    else:
        # Handle unexpected model IDs safely
        rate_limit_store["counts"][model_id] = 1

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

# Style Templates with Categories
STYLES = {
    # === Group: Cinematic (Movies & TV) ===
    "wes_anderson": {
        "name": "Wes Anderson (Grand Budapest)",
        "group": "Cinematic",
        "prompt_suffix": ", in the style of Wes Anderson, symmetrical composition, pastel colors, retro aesthetic, highly detailed, whimsical, cinematic lighting"
    },
    "cyberpunk_2077": {
        "name": "Cyberpunk 2077 (Neon Noir)",
        "group": "Cinematic",
        "prompt_suffix": ", cyberpunk 2077 style, neon lights, night city, rain, high tech low life, chromatic aberration, volumetric lighting, futuristic"
    },
    "ghibli": {
        "name": "Studio Ghibli (Anime)",
        "group": "Cinematic",
        "prompt_suffix": ", Studio Ghibli style, Hayao Miyazaki, anime, vibrant colors, peaceful atmosphere, detailed background art, hand drawn style"
    },
    "dune": {
        "name": "Dune (Epic Sci-Fi)",
        "group": "Cinematic",
        "prompt_suffix": ", Dune movie style, vast desert landscape, brutalist architecture, muted earth tones, cinematic scale, epic atmosphere, Denis Villeneuve"
    },
    
    # === Group: Art Styles ===
    "van_gogh": {
        "name": "Van Gogh (Starry Night)",
        "group": "Art Styles",
        "prompt_suffix": ", in the style of Vincent van Gogh, thick impasto brushstrokes, swirling patterns, vibrant blue and yellow colors, expressive oil painting"
    },
    "ukiyo_e": {
        "name": "Ukiyo-e (Japanese Woodblock)",
        "group": "Art Styles",
        "prompt_suffix": ", Ukiyo-e style, Japanese woodblock print, flat colors, bold outlines, Hokusai style, traditional japanese art"
    },
    "pixel_art": {
        "name": "Pixel Art (Retro Game)",
        "group": "Art Styles",
        "prompt_suffix": ", pixel art, 8-bit style, retro video game, low resolution, dithering, vibrant colors"
    },
    "watercolor": {
        "name": "Watercolor (Soft)",
        "group": "Art Styles",
        "prompt_suffix": ", watercolor painting, soft edges, paper texture, wet-on-wet technique, dreamy atmosphere, artistic"
    },

    # === Group: Photography ===
    "polaroid": {
        "name": "Polaroid (Vintage)",
        "group": "Photography",
        "prompt_suffix": ", polaroid photo, vintage aesthetic, film grain, soft focus, flash photography, nostalgia, 1990s style"
    },
    "macro": {
        "name": "Macro Photography (Close-up)",
        "group": "Photography",
        "prompt_suffix": ", macro photography, extreme close-up, high detail, shallow depth of field, bokeh background, sharp focus"
    },
    "drone": {
        "name": "Drone Shot (Aerial)",
        "group": "Photography",
        "prompt_suffix": ", aerial view, drone photography, bird's eye view, high angle shot, vast landscape, epic scale"
    },

    # === Group: 3D & Digital ===
    "3d_render": {
        "name": "3D Render (Octane)",
        "group": "3D & Digital",
        "prompt_suffix": ", 3d render, octane render, unreal engine 5, ray tracing, highly detailed, photorealistic, 8k resolution"
    },
    "low_poly": {
        "name": "Low Poly (Minimalist)",
        "group": "3D & Digital",
        "prompt_suffix": ", low poly style, minimalist 3d, sharp edges, flat shading, geometric shapes, isometric view"
    },

    # === Special ===
    "custom": {
        "name": "✨ Custom Style (Enter your own)",
        "group": "Special",
        "prompt_suffix": "" # Placeholder, will be replaced by user input
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

    # Check for magic flag to skip enhancement
    if "--raw" in original_prompt:
        print("Raw mode detected, skipping enhancement/style")
        return original_prompt.replace("--raw", "").strip()
    
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
    data = request.json
    
    # 1. Simple Authentication Check
    if ACCESS_CODE:
        user_code = data.get('access_code')
        if user_code != ACCESS_CODE:
            return jsonify({"error": "Invalid Access Code"}), 401

    if not API_KEY:
        return jsonify({"error": "API Key not configured in .env"}), 500

    user_prompt = data.get('prompt')
    model_id = data.get('model_id', 'model_2') # Default to model_2 (cheaper one)
    style_id = data.get('style_id', 'none')
    
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # 2. Input Validation (Length Check)
    if len(user_prompt) > MAX_PROMPT_LENGTH:
        return jsonify({"error": f"Prompt too long ({len(user_prompt)} chars). Max allowed: {MAX_PROMPT_LENGTH}"}), 400

    # 3. Rate Limit Check (Per Model)
    allowed, message = check_rate_limit(model_id)
    if not allowed:
        return jsonify({"error": message}), 429

    # Get model configuration
    selected_model = MODELS.get(model_id)
    if not selected_model or not selected_model["endpoint"]:
        return jsonify({"error": "Invalid model selected or model not configured"}), 400

    # 4. Prompt Processing Pipeline
    start_time = time.time()
    # Magic word to skip enhancement
    MAGIC_WORD = "#原图"
    is_raw_mode = MAGIC_WORD in user_prompt
    
    if is_raw_mode:
        # Raw Mode: Skip enhancement and style templates
        print(f"Raw mode detected: {user_prompt}")
        final_prompt = user_prompt.replace(MAGIC_WORD, "").strip()
        enhanced = False
    else:
        # Normal Mode: Apply enhancement and style
        if TEXT_API_KEY and style_id == "none":
            # Only use LLM enhancement if no specific style is selected
            # (To avoid conflicting instructions)
            final_prompt = enhance_prompt(user_prompt, "")
            enhanced = True
        else:
            # Use style template logic
            style_obj = STYLES.get(style_id)
            suffix = style_obj['prompt_suffix'] if style_obj else ""
            final_prompt = enhance_prompt(user_prompt, suffix)
            enhanced = False if style_id == "none" else True

    print(f"Final Prompt: {final_prompt}")

    # Calculate simple token estimate (approx 4 chars per token)
    estimated_prompt_tokens = len(final_prompt) // 4

    try:
        print(f"Generating with Model: {selected_model['name']} ({selected_model['endpoint']})")
        print(f"Size: {selected_model['size']}")

        # Step 2: Call the Image Generation API via OpenAI SDK
        response = client.images.generate(
            model=selected_model["endpoint"],
            prompt=final_prompt,
            size=selected_model["size"], 
        )
        
        # Increment counter only on success
        increment_rate_limit(model_id)
        
        end_time = time.time()
        elapsed_time = round(end_time - start_time, 2)
        
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
                "style_used": style_name,
                "debug_info": {
                    "time_elapsed": f"{elapsed_time}s",
                    "prompt_length": len(final_prompt),
                    "estimated_tokens": estimated_prompt_tokens
                }
            })
        else:
            return jsonify({"error": "No image data returned from API"}), 500

    except Exception as e:
        print(f"Error generating image: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
