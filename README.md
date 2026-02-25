# AI Image Generator (Seedream/BytePlus)

A simple, extensible web application for generating images using BytePlus ModelArk (Seedream 5.0 Lite & 4.0) via the OpenAI-compatible API.

This project demonstrates how to:
- Connect to BytePlus ModelArk using the standard OpenAI Python SDK.
- Configure multiple models with different parameters (e.g., resolution constraints).
- Provide a clean, modern UI for model selection and image generation.

## Features

- **Multi-Model Support**: Switch seamlessly between different models (e.g., High Quality vs. Fast/Cheap).
- **Smart Configuration**: Automatically adjusts image resolution requirements based on the selected model (e.g., 1920x1920 for Seedream 5.0 Lite).
- **Clean UI**: Responsive web interface built with Vanilla JS and CSS.
- **Extensible Backend**: Flask-based backend ready for adding "Agentic" workflows (prompt rewriting, style transfer, etc.).

## Prerequisites

- Python 3.8+
- A BytePlus Account with ModelArk access.
- API Key and Endpoint IDs for the models you wish to use.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/test_pic_gen.git
    cd test_pic_gen
    ```

2.  **Create and activate a virtual environment (Recommended):**
    ```bash
    # Using venv
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

    # OR using Conda
    conda create -n pic_gen python=3.10
    conda activate pic_gen
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration:**
    Copy the example environment file and update it with your credentials.
    ```bash
    cp .env.example .env
    ```
    
    Open `.env` and fill in your details:
    ```env
    IMAGE_GEN_API_KEY=your_actual_api_key
    ARK_BASE_URL=https://ark.ap-southeast.bytepluses.com/api/v3

    # Configure your models
    MODEL_1_NAME=Seedream 5.0 Lite
    MODEL_1_ENDPOINT=ep-202xxxxx-xxxxx
    MODEL_1_SIZE=1920x1920

    MODEL_2_NAME=Seedream 4.0
    MODEL_2_ENDPOINT=ep-202xxxxx-xxxxx
    MODEL_2_SIZE=1024x1024
    ```

## Usage

1.  **Start the server:**
    ```bash
    python app.py
    ```

2.  **Open your browser:**
    Navigate to `http://127.0.0.1:5000`.

3.  **Generate Images:**
    - Select a model from the dropdown.
    - Enter a prompt description.
    - Click "Generate Image".

## Project Structure

```text
.
├── app.py              # Main Flask application & API logic
├── .env                # Environment variables (API Keys) - DO NOT COMMIT
├── .env.example        # Template for environment variables
├── requirements.txt    # Python dependencies
├── static/             # Frontend assets
│   ├── style.css       # Styling
│   └── script.js       # Frontend logic (API calls, UI updates)
└── templates/          # HTML templates
    └── index.html      # Main page structure
```

## Future Roadmap

- [ ] **Style Selector**: Add preset styles (Cyberpunk, Watercolor, Anime) to the UI.
- [ ] **Prompt Enhancement**: Integrate an LLM Agent to rewrite and optimize user prompts automatically.
- [ ] **Image-to-Image**: Support uploading reference images for style transfer or variations.

## License

MIT License
