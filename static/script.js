document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generateBtn');
    const promptInput = document.getElementById('promptInput');
    const modelSelect = document.getElementById('modelSelect');
    const loadingDiv = document.getElementById('loading');
    const resultSection = document.getElementById('resultSection');
    const generatedImage = document.getElementById('generatedImage');
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    const finalPromptDisplay = document.getElementById('finalPromptDisplay');

    // Fetch and populate models on load
    fetchModels();

    async function fetchModels() {
        try {
            const response = await fetch('/config');
            const data = await response.json();
            
            // Clear existing options
            modelSelect.innerHTML = '';
            
            if (data.models && data.models.length > 0) {
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.name;
                    // Default to model_2 (cheaper) if available, logic can be adjusted
                    if (model.id === 'model_2') {
                        option.selected = true;
                    }
                    modelSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Failed to load models:', error);
            // Fallback option
            const option = document.createElement('option');
            option.value = 'model_2';
            option.textContent = 'Default Model';
            modelSelect.appendChild(option);
        }
    }

    generateBtn.addEventListener('click', async () => {
        const prompt = promptInput.value.trim();
        const selectedModel = modelSelect.value;
        
        if (!prompt) {
            alert('Please enter a prompt first.');
            return;
        }

        // Reset UI
        generateBtn.disabled = true;
        loadingDiv.classList.remove('hidden');
        resultSection.classList.add('hidden');
        errorSection.classList.add('hidden');

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    prompt: prompt,
                    model_id: selectedModel 
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate image');
            }

            // Success
            generatedImage.src = data.image_url;
            finalPromptDisplay.innerHTML = `<strong>Model:</strong> ${data.model_used}<br><strong>Prompt used:</strong> "${data.final_prompt}"`;
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
