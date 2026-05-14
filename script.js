// ColdSync AI - Investigative Logic
const imageInput = document.getElementById('image-input');
const dropZone = document.getElementById('drop-zone');
const imagePreview = document.getElementById('image-preview');
const previewContainer = document.getElementById('preview-container');
const analyzeBtn = document.getElementById('analyze-btn');
const pixelScanner = document.getElementById('pixel-scanner');
const moInput = document.getElementById('mo-input');
const resultsContainer = document.getElementById('results-container');
const synthesisCard = document.getElementById('synthesis-card');
const synthesisContent = document.getElementById('synthesis-content');
const emptyState = document.getElementById('empty-state');

let selectedFiles = [];

// Handle Image Selection
dropZone.addEventListener('click', () => imageInput.click());

imageInput.addEventListener('change', (e) => {
    selectedFiles = Array.from(e.target.files);
    if (selectedFiles.length > 0) {
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            previewContainer.classList.remove('hidden');
        };
        reader.readAsDataURL(selectedFiles[0]); // Preview first image
    }
});

// Run Investigative Analysis
analyzeBtn.addEventListener('click', async () => {
    const moText = moInput.value.trim();
    if (selectedFiles.length === 0 || !moText) {
        alert("CRITICAL: Investigative data incomplete. Image evidence and M.O. narrative required.");
        return;
    }

    // UI Feedback: Start Scanning
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `<span>PROCESSING EVIDENCE...</span><i data-lucide="refresh-cw" class="w-5 h-5 animate-spin"></i>`;
    lucide.createIcons();
    pixelScanner.classList.add('scan-active');

    const formData = new FormData();
    formData.append('text_summary', moText);
    selectedFiles.forEach(file => {
        formData.append('scene_images', file);
    });

    try {
        const response = await fetch('http://127.0.0.1:8000/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API Error ${response.status}: ${errorText || response.statusText}`);
        }

        const data = await response.json();
        renderResults(data);

    } catch (error) {
        console.error("NETWORK/API ERROR:", error);
        alert(`INVESTIGATION FAILED: ${error.message}\n\nCheck browser console for details.`);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = `<span>RUN INVESTIGATIVE ANALYSIS</span><i data-lucide="zap" class="w-5 h-5"></i>`;
        lucide.createIcons();
        pixelScanner.classList.remove('scan-active');
    }
});

// Render Investigative Feed
function renderResults(data) {
    emptyState.classList.add('hidden');
    resultsContainer.innerHTML = ''; // Clear previous results

    // 1. Forensic Synthesis with Formatting
    synthesisCard.classList.remove('hidden');
    
    // Process text to handle bullets and bolding before typing
    let formattedText = data.forensic_synthesis;
    
    // Convert * or - bullet points to list items
    if (formattedText.includes('*') || formattedText.includes('-')) {
        const lines = formattedText.split(/\n/).filter(line => line.trim() !== '');
        let htmlOutput = '<ul class="space-y-4">';
        lines.forEach(line => {
            const cleanLine = line.replace(/^[\s*-]+/, '').trim();
            if (cleanLine) {
                // Bold anything before a colon
                const boldedLine = cleanLine.replace(/^([^:]+):/, '<strong>$1:</strong>');
                htmlOutput += `<li>${boldedLine}</li>`;
            }
        });
        htmlOutput += '</ul>';
        synthesisContent.innerHTML = htmlOutput;
    } else {
        synthesisContent.textContent = formattedText;
    }

    // 2. Result Cards
    if (data.top_matches.length === 0) {
        resultsContainer.innerHTML = `
            <div class="p-6 bg-[#151921] border border-[#FF4B4B]/30 rounded-xl text-center">
                <p class="text-sm text-[#FF4B4B] font-bold">NO CONFIDENT MATCHES IDENTIFIED IN ARCHIVES</p>
            </div>`;
        return;
    }

    data.top_matches.forEach((match, index) => {
        const card = document.createElement('div');
        card.className = `result-card bg-[#151921] border border-[#2D343F] rounded-xl overflow-hidden shadow-xl mb-4 ${match.divergence_flag ? 'divergence-alert border-[#FF4B4B]/50' : ''}`;
        card.style.animationDelay = `${index * 0.1}s`;

        card.innerHTML = `
            ${match.divergence_flag ? `
                <div class="bg-[#FF4B4B] text-black text-[10px] font-black py-1 px-4 text-center tracking-[0.2em]">
                    🚨 CRITICAL DIVERGENCE: POSSIBLE STAGED SCENE / COPYCAT DETECTED
                </div>
            ` : ''}
            
            <div class="p-6">
                <div class="flex items-center justify-between mb-6">
                    <div>
                        <h4 class="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Case ID</h4>
                        <p class="text-[#00D2FF] font-mono text-lg font-bold">#${match.case_id}</p>
                    </div>
                    <div class="flex items-center gap-4">
                        <div class="text-right">
                            <h4 class="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Combined Score</h4>
                            <p class="text-2xl font-black text-[#00D2FF]">${match.combined_score}%</p>
                        </div>
                        <div class="metric-ring">
                            <svg width="60" height="60">
                                <circle class="bg" cx="30" cy="30" r="28"></circle>
                                <circle class="progress" cx="30" cy="30" r="28" style="stroke-dashoffset: ${176 - (176 * match.combined_score / 100)}"></circle>
                            </svg>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-3 gap-6">
                    <div class="space-y-2">
                        <p class="text-[10px] font-bold text-gray-500 uppercase">Input Evidence</p>
                        <div class="aspect-square bg-black rounded-lg overflow-hidden border border-[#2D343F]">
                            <img src="${URL.createObjectURL(selectedFiles[0])}" class="w-full h-full object-cover opacity-60">
                        </div>
                    </div>
                    <div class="space-y-2">
                        <p class="text-[10px] font-bold text-gray-500 uppercase">Archived Match</p>
                        <div class="aspect-square bg-black rounded-lg overflow-hidden border border-[#2D343F]">
                            <img src="${match.image_path ? `http://127.0.0.1:8000/${match.image_path}` : 'https://via.placeholder.com/400?text=No+Image'}" class="w-full h-full object-cover">
                        </div>
                    </div>
                    <div class="flex flex-col justify-between">
                        <div class="space-y-4">
                            <div>
                                <p class="text-[10px] font-bold text-gray-500 uppercase mb-2">Forensic Metrics</p>
                                <div class="space-y-2">
                                    <div class="flex justify-between text-[10px]">
                                        <span>TEXT SIMILARITY</span>
                                        <span class="text-[#00D2FF]">${match.text_score}%</span>
                                    </div>
                                    <div class="w-full bg-[#2D343F] h-1 rounded-full">
                                        <div class="bg-[#00D2FF] h-full rounded-full" style="width: ${match.text_score}%"></div>
                                    </div>
                                    <div class="flex justify-between text-[10px]">
                                        <span>VISUAL MATCH</span>
                                        <span class="text-[#00D2FF]">${match.visual_score}%</span>
                                    </div>
                                    <div class="w-full bg-[#2D343F] h-1 rounded-full">
                                        <div class="bg-[#00D2FF] h-full rounded-full" style="width: ${match.visual_score}%"></div>
                                    </div>
                                </div>
                            </div>
                            <div class="text-[11px] leading-relaxed text-gray-400 border-l-2 border-[#2D343F] pl-3 italic">
                                ${match.text_summary}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        resultsContainer.appendChild(card);
    });
}

// Typing Effect Helper
function typeWriter(text, element) {
    element.innerHTML = '';
    let i = 0;
    const speed = 20; // ms per character
    
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}
