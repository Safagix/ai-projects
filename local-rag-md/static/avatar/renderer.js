// ══════════════════════════════════════════════════════════
// Avatar ASCII Renderer & Audio Sync
// ══════════════════════════════════════════════════════════

// Temporary Placeholder Frames (Will be replaced by generated anime frames)
window.ASCII_FRAMES = window.ASCII_FRAMES || [
    `
      /\\_/\\      
     ( o.o )     
      > ^ <      
    `,
    `
      /\\_/\\      
     ( o_o )     
      > o <      
    `,
    `
      /\\_/\\      
     ( oO )     
      > O <      
    `
];

(function() {
    // ── UI Elements ──
    const viewBtn = document.getElementById('viewEiraBtn');
    const avatarContainer = document.getElementById('avatarContainer');
    const messagesContainer = document.getElementById('messages');
    const canvas = document.getElementById('asciiCanvas');
    
    // ── Audio Context State ──
    let audioCtx = null;
    let analyser = null;
    let source = null;
    let dataArray = null;
    let isPlaying = false;
    let animationFrameId = null;

    // Toggle Avatar View Mode
    if (viewBtn) {
        viewBtn.addEventListener('click', () => {
            const isAvatarMode = !avatarContainer.classList.contains('hidden');
            
            if (isAvatarMode) {
                // Switch back to chat
                avatarContainer.classList.add('hidden');
                // We no longer hide messages when viewing avatar since it's in the sidebar
                // messagesContainer.classList.remove('hidden');
                viewBtn.classList.remove('active');
            } else {
                // Switch to avatar
                avatarContainer.classList.remove('hidden');
                // We no longer hide messages when viewing avatar
                // messagesContainer.classList.add('hidden');
                viewBtn.classList.add('active');
                
                // Show default frame
                if (!isPlaying) {
                    canvas.textContent = window.ASCII_FRAMES[0];
                }
                
                // Calculate scale
                setTimeout(fitToContainer, 10);
            }
        });
    }

    function fitToContainer() {
        if (!avatarContainer || !canvas || avatarContainer.classList.contains('hidden')) return;
        
        // We know the ASCII art is 80 chars wide. With JetBrains Mono 6px, it's roughly 288px wide.
        // We calculate scale purely based on container width.
        const containerWidth = avatarContainer.clientWidth;
        if (containerWidth > 0) {
            // Approx width of 80 full block characters at 6px is 80*3.6 = ~288px
            // Let's just measure the scroll width instead when scale is 1
            canvas.style.transform = 'scale(1)';
            const artWidth = canvas.scrollWidth || 300;
            const scale = containerWidth / artWidth;
            canvas.style.transform = `scale(${scale * 0.95})`; // 0.95 for tiny padding
            canvas.style.transformOrigin = 'center';
        }
    }
    
    window.addEventListener('resize', fitToContainer);

    // ── Audio Sync Logic ──
    window.playAvatarAudio = async function(audioUrl) {
        try {
            // Lazy init AudioContext
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioCtx.createAnalyser();
                analyser.fftSize = 256;
                const bufferLength = analyser.frequencyBinCount;
                dataArray = new Uint8Array(bufferLength);
            }
            
            // Resume contextual audio if suspended (Chrome policy)
            if (audioCtx.state === 'suspended') {
                await audioCtx.resume();
            }

            // Fetch the audio file
            const response = await fetch(audioUrl);
            const arrayBuffer = await response.arrayBuffer();
            const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);

            // Connect graph
            source = audioCtx.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(analyser);
            analyser.connect(audioCtx.destination);
            
            source.onended = () => {
                isPlaying = false;
                cancelAnimationFrame(animationFrameId);
                canvas.textContent = window.ASCII_FRAMES[0]; // Reset to idle frame
            };

            source.start(0);
            isPlaying = true;

            // Start animation loop
            renderLoop();

        } catch (error) {
            console.error("Error playing avatar audio:", error);
        }
    };

    function renderLoop() {
        if (!isPlaying) return;

        animationFrameId = requestAnimationFrame(renderLoop);

        // Get volume amplitude from analyser
        analyser.getByteFrequencyData(dataArray);
        
        // Calculate average volume (we can map to vocal range specifically)
        let sum = 0;
        // Vocal range approx in lower half of bins
        for(let i = 0; i < dataArray.length / 2; i++) {
            sum += dataArray[i];
        }
        let average = sum / (dataArray.length / 2);

        // Normalize amplitude to frame index (0-3)
        // Adjust these thresholds based on true output
        let frameIndex = 0;
        if (average > 40) {
            frameIndex = 3; // Mouth wide open
        } else if (average > 25) {
            frameIndex = 2; // Mouth half open
        } else if (average > 10) {
            frameIndex = 1; // Mouth slightly open
        } else {
            frameIndex = 0; // Mouth closed
        }

        // Only update DOM if frame changed or avatar is visible
        if (!avatarContainer.classList.contains('hidden')) {
            canvas.textContent = window.ASCII_FRAMES[frameIndex];
        }
    }
    
    // Initial display
    if (canvas) {
        canvas.textContent = window.ASCII_FRAMES[0];
    }
})();
