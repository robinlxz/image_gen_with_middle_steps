document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generateBtn');
    const promptInput = document.getElementById('promptInput');
    const loadingDiv = document.getElementById('loading');
    const resultSection = document.getElementById('resultSection');
    const generatedImage = document.getElementById('generatedImage');
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    const finalPromptDisplay = document.getElementById('finalPromptDisplay');

    generateBtn.addEventListener('click', async () => {
        const prompt = promptInput.value.trim();
        
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
                body: JSON.stringify({ prompt: prompt }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate image');
            }

            // Success
            generatedImage.src = data.image_url;
            finalPromptDisplay.textContent = `Prompt used: "${data.final_prompt}"`; // Show the potentially modified prompt
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
