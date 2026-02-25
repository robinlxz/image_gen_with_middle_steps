document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generateBtn');
    const promptInput = document.getElementById('promptInput');
    const modelSelect = document.getElementById('modelSelect');
    const styleOptionsContainer = document.getElementById('styleOptions');
    const selectedStyleInput = document.getElementById('selectedStyle');
    const loadingDiv = document.getElementById('loading');
    const resultSection = document.getElementById('resultSection');
    const generatedImage = document.getElementById('generatedImage');
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    const finalPromptDisplay = document.getElementById('finalPromptDisplay');
    const debugSection = document.getElementById('debugSection');
    const debugFinalPrompt = document.getElementById('debugFinalPrompt');

    // Fetch and populate models & styles on load
    fetchConfig();

    async function fetchConfig() {
        try {
            const response = await fetch('/config');
            const data = await response.json();
            
            // 1. Populate Models
            modelSelect.innerHTML = '';
            if (data.models && data.models.length > 0) {
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.name;
                    if (model.id === 'model_2') option.selected = true;
                    modelSelect.appendChild(option);
                });
            }

            // 2. Populate Styles
            styleOptionsContainer.innerHTML = '';
            if (data.styles && data.styles.length > 0) {
                data.styles.forEach(style => {
                    const btn = document.createElement('div');
                    btn.className = 'style-option';
                    btn.textContent = style.name;
                    btn.dataset.value = style.id;
                    
                    // Default selection
                    if (style.id === 'none') {
                        btn.classList.add('selected');
                        selectedStyleInput.value = style.id;
                    }

                    // Click handler
                    btn.addEventListener('click', () => {
                        // Deselect all
                        document.querySelectorAll('.style-option').forEach(b => b.classList.remove('selected'));
                        // Select clicked
                        btn.classList.add('selected');
                        selectedStyleInput.value = style.id;
                    });

                    styleOptionsContainer.appendChild(btn);
                });
            }

        } catch (error) {
            console.error('Failed to load config:', error);
            // Fallback UI if config fails
        }
    }

    generateBtn.addEventListener('click', async () => {
        const prompt = promptInput.value.trim();
        const selectedModel = modelSelect.value;
        const selectedStyle = selectedStyleInput.value;
        
        if (!prompt) {
            alert('Please enter a prompt first.');
            return;
        }

        // Reset UI
        generateBtn.disabled = true;
        loadingDiv.classList.remove('hidden');
        resultSection.classList.add('hidden');
        errorSection.classList.add('hidden');
        debugSection.classList.add('hidden');

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    prompt: prompt,
                    model_id: selectedModel,
                    style_id: selectedStyle
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate image');
            }

            // Success
            generatedImage.src = data.image_url;
            finalPromptDisplay.innerHTML = `
                <strong>Model:</strong> ${data.model_used}<br>
                <strong>Style:</strong> ${data.style_used || 'Default'}<br>
            `;
            
            // Populate Debug Info
            debugFinalPrompt.textContent = data.final_prompt;
            debugSection.classList.remove('hidden');

            resultSection.classList.remove('hidden');

        } catch (error) {
            console.error('Error:', error);
            errorMessage.textContent = error.message;
            errorSection.classList.remove('hidden');
        } finally {
            generateBtn.disabled = false;
            loadingDiv.classList.add('hidden');
        }
    });
});
