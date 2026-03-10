document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generateBtn');
    const promptInput = document.getElementById('promptInput');
    const accessCodeInput = document.getElementById('accessCode');
    const modelSelect = document.getElementById('modelSelect');
    const categorySelect = document.getElementById('categorySelect');
    const styleSelect = document.getElementById('styleSelect');
    const customStyleContainer = document.getElementById('customStyleContainer');
    const customStyleInput = document.getElementById('customStyleInput');
    const surpriseBtn = document.getElementById('surpriseBtn');
    
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

    // Gallery Elements
    const galleryBtn = document.getElementById('galleryBtn');
    const closeGalleryBtn = document.getElementById('closeGalleryBtn');
    const gallerySection = document.getElementById('gallerySection');
    const galleryGrid = document.getElementById('galleryGrid');
    
    // Modal Elements
    const imageModal = document.getElementById('imageModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const modalImage = document.getElementById('modalImage');
    const modalPrompt = document.getElementById('modalPrompt');
    const modalDate = document.getElementById('modalDate');
    const modalStyle = document.getElementById('modalStyle');

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

    // Handle Surprise Me Button
    surpriseBtn.addEventListener('click', async () => {
        // Disable button to prevent spamming
        surpriseBtn.disabled = true;
        const originalText = surpriseBtn.innerHTML;
        surpriseBtn.innerHTML = '🎲 Rolling...';
        promptInput.value = 'Thinking of something creative...';

        try {
            // Logic: Always pick a random style for "Surprise Me"
            // This ensures a fresh surprise every time, even if a style is already selected.
            
            let currentStyleId = 'none';

            if (allStyles.length > 0) {
                // Filter valid styles (exclude 'none' and 'custom')
                const validStyles = allStyles.filter(s => s.id !== 'none' && s.id !== 'custom');
                
                if (validStyles.length > 0) {
                    // Pick random style
                    const randomStyle = validStyles[Math.floor(Math.random() * validStyles.length)];
                    currentStyleId = randomStyle.id;

                    // Update UI to reflect random style choice
                    // 1. Set Category
                    if (randomStyle.group) {
                        categorySelect.value = randomStyle.group;
                        // Important: Manually trigger the category change logic to repopulate style dropdown
                        populateStyles(allStyles, randomStyle.group);
                    } else {
                        categorySelect.value = 'all';
                        populateStyles(allStyles, 'all');
                    }
                    
                    // 2. Set Style
                    styleSelect.value = randomStyle.id;
                    
                    // 3. Handle Custom Input visibility
                    if (randomStyle.id === 'custom') {
                        customStyleContainer.classList.remove('hidden');
                    } else {
                        customStyleContainer.classList.add('hidden');
                    }
                }
            }

            // Call Backend
            const response = await fetch('/random_prompt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ style_id: currentStyleId })
            });

            const data = await response.json();
            
            if (data.prompt) {
                promptInput.value = data.prompt;
            } else {
                promptInput.value = "Failed to get inspiration. Try again!";
            }

        } catch (error) {
            console.error('Surprise failed:', error);
            promptInput.value = "An error occurred. Please try again.";
        } finally {
            surpriseBtn.disabled = false;
            surpriseBtn.innerHTML = originalText;
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
            
            // Save to Gallery History
            saveToHistory({
                url: data.image_url,
                prompt: data.original_prompt,
                model: data.model_used,
                style: data.style_used,
                timestamp: new Date().toISOString()
            });

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

    // === Gallery Logic ===

    // Toggle Gallery View
    galleryBtn.addEventListener('click', () => {
        gallerySection.classList.remove('hidden');
        loadGallery();
        // Scroll to gallery
        gallerySection.scrollIntoView({ behavior: 'smooth' });
    });

    closeGalleryBtn.addEventListener('click', () => {
        gallerySection.classList.add('hidden');
    });

    // Save item to LocalStorage
    function saveToHistory(item) {
        const history = JSON.parse(localStorage.getItem('image_history') || '[]');
        // Add ID
        item.id = Date.now().toString();
        // Add to beginning
        history.unshift(item);
        // Limit to 50 items in local history (ECS keeps more, but browser keeps recent)
        if (history.length > 50) history.pop();
        
        localStorage.setItem('image_history', JSON.stringify(history));
    }

    // Load and Render Gallery
    function loadGallery() {
        const history = JSON.parse(localStorage.getItem('image_history') || '[]');
        galleryGrid.innerHTML = '';

        if (history.length === 0) {
            galleryGrid.innerHTML = '<p class="text-gray-500 col-span-full text-center py-8">No images in your gallery yet. Generate some!</p>';
            return;
        }

        history.forEach(item => {
            const card = document.createElement('div');
            card.className = 'bg-gray-50 rounded shadow overflow-hidden relative group';
            
            // Format Date
            const date = new Date(item.timestamp).toLocaleDateString() + ' ' + new Date(item.timestamp).toLocaleTimeString();

            card.innerHTML = `
                <img src="${item.url}" alt="${item.prompt}" class="w-full h-48 object-cover cursor-pointer hover:opacity-90 transition" onclick="openModal('${item.url}', '${item.prompt.replace(/'/g, "\\'")}', '${date}', '${item.style}')">
                <div class="p-3">
                    <p class="text-sm text-gray-800 truncate" title="${item.prompt}">${item.prompt}</p>
                    <div class="flex justify-between items-center mt-2 text-xs text-gray-500">
                        <span>${item.style || 'Default'}</span>
                        <button class="text-red-500 hover:text-red-700 delete-btn" data-id="${item.id}">Delete</button>
                    </div>
                </div>
            `;
            
            // Add Delete Event
            const deleteBtn = card.querySelector('.delete-btn');
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if(confirm('Remove this image from your history?')) {
                    deleteFromHistory(item.id);
                }
            });

            galleryGrid.appendChild(card);
        });
    }

    // Delete item
    function deleteFromHistory(id) {
        let history = JSON.parse(localStorage.getItem('image_history') || '[]');
        history = history.filter(item => item.id !== id);
        localStorage.setItem('image_history', JSON.stringify(history));
        loadGallery(); // Re-render
    }

    // === Modal Logic ===
    window.openModal = function(url, prompt, date, style) {
        modalImage.src = url;
        modalPrompt.textContent = prompt;
        modalDate.textContent = date;
        modalStyle.textContent = style;
        imageModal.classList.remove('hidden');
    };

    closeModalBtn.addEventListener('click', () => {
        imageModal.classList.add('hidden');
    });

    // Close modal on click outside
    imageModal.addEventListener('click', (e) => {
        if (e.target === imageModal) {
            imageModal.classList.add('hidden');
        }
    });

});
