document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generateBtn');
    const promptInput = document.getElementById('promptInput');
    const accessCodeInput = document.getElementById('accessCode');
    const modelSelect = document.getElementById('modelSelect');
    const categorySelect = document.getElementById('categorySelect');
    const styleSelect = document.getElementById('styleSelect');
    const customStyleContainer = document.getElementById('customStyleContainer');
    const customStyleInput = document.getElementById('customStyleInput');
    
    const loadingDiv = document.getElementById('loading');
    const resultSection = document.getElementById('resultSection');
    const generatedImage = document.getElementById('generatedImage');
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    const finalPromptDisplay = document.getElementById('finalPromptDisplay');
    const debugSection = document.getElementById('debugSection');
    const debugFinalPrompt = document.getElementById('debugFinalPrompt');
    const debugOriginalPrompt = document.getElementById('debugOriginalPrompt');
    const debugTime = document.getElementById('debugTime');
    const debugTokens = document.getElementById('debugTokens');

    let allStyles = []; // Store fetched styles globally

    // Load models and styles on startup
    loadConfig();

    async function loadConfig() {
        try {
            const response = await fetch('/config');
            const data = await response.json();
            
            // Populate Models
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

            // Store and populate Styles
            allStyles = data.styles || [];
            populateCategories(allStyles);
            populateStyles(allStyles); // Initial population (All)

        } catch (error) {
            console.error('Error loading config:', error);
            alert('Failed to load configuration. Is the server running?');
        }
    }

    // Populate Category Selector
    function populateCategories(styles) {
        const categories = new Set(styles.map(s => s.group).filter(g => g));
        
        // Add "All" option
        categorySelect.innerHTML = '<option value="all">All Categories</option>';
        
        // Add specific categories
        Array.from(categories).sort().forEach(cat => {
            const option = document.createElement('option');
            option.value = cat;
            option.textContent = cat;
            categorySelect.appendChild(option);
        });
    }

    // Populate Style Selector (Filtered)
    function populateStyles(styles, categoryFilter = 'all') {
        styleSelect.innerHTML = '';
        
        // Add Default/None option always
        const defaultOption = document.createElement('option');
        defaultOption.value = 'none';
        defaultOption.textContent = 'No Style (Default)';
        styleSelect.appendChild(defaultOption);

        // Filter styles
        let filteredStyles = styles;
        if (categoryFilter !== 'all') {
            filteredStyles = styles.filter(s => s.group === categoryFilter);
        }

        // Group logic (keep optgroups if showing 'all', or just list if specific category)
        if (categoryFilter === 'all') {
            const groups = {};
            filteredStyles.forEach(style => {
                if (style.id === 'none') return;
                const groupName = style.group || 'Other';
                if (!groups[groupName]) groups[groupName] = [];
                groups[groupName].push(style);
            });

            for (const [groupName, groupStyles] of Object.entries(groups)) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = groupName;
                groupStyles.forEach(style => {
                    const option = document.createElement('option');
                    option.value = style.id;
                    option.textContent = style.name;
                    optgroup.appendChild(option);
                });
                styleSelect.appendChild(optgroup);
            }
        } else {
            // Flat list for specific category
            filteredStyles.forEach(style => {
                if (style.id === 'none') return;
                const option = document.createElement('option');
                option.value = style.id;
                option.textContent = style.name;
                styleSelect.appendChild(option);
            });
        }
    }

    // Handle Category Change
    categorySelect.addEventListener('change', () => {
        const selectedCategory = categorySelect.value;
        populateStyles(allStyles, selectedCategory);
        // Reset custom input visibility
        customStyleContainer.classList.add('hidden');
    });

    // Handle Custom Style Visibility
    styleSelect.addEventListener('change', () => {
        if (styleSelect.value === 'custom') {
            customStyleContainer.classList.remove('hidden');
            customStyleInput.focus();
        } else {
            customStyleContainer.classList.add('hidden');
        }
    });

    // Handle Generate Button Click
    generateBtn.addEventListener('click', async () => {
        const prompt = promptInput.value.trim();
        const accessCode = accessCodeInput.value.trim();
        const selectedModel = modelSelect.value;
        const selectedStyle = styleSelect.value;
        const customStyle = customStyleInput.value.trim();
        
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
                    access_code: accessCode,
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
            debugOriginalPrompt.textContent = data.original_prompt;
            debugFinalPrompt.textContent = data.final_prompt;
            
            if (data.debug_info) {
                debugTime.textContent = data.debug_info.time_elapsed;
                debugTokens.textContent = data.debug_info.estimated_tokens;
            }
            
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
