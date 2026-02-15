(function () {
    // Configuration
    const CONFIG = {
        chars: 'Velar',
        fontSize: 14,
        speed: 75,
        color: 'rgba(255, 255, 255, 0.75)',
        bg: 'rgba(15, 23, 42, 0.05)'
    };

    // State
    let canvas = null;
    let ctx = null;
    let width = 0;
    let height = 0;
    let columns = 0;
    let drops = [];
    let lastDraw = 0;

    function init(c) {
        canvas = c;
        ctx = canvas.getContext('2d');
        resize();

        // Initialize drops if empty
        if (drops.length === 0) {
            for (let x = 0; x < columns; x++) drops[x] = 1;
        }
        console.log("MATRIX: Initialized on new canvas");
    }

    function resize() {
        if (!canvas) return;
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
        columns = width / CONFIG.fontSize;

        // Preserve drops if resizing, or reset if drastic change?
        // Simple reset for robustness
        drops = [];
        for (let x = 0; x < columns; x++) drops[x] = 1;
    }

    function draw(timestamp) {
        // animation frame loop
        requestAnimationFrame(draw);

        // Throttle speed
        if (timestamp - lastDraw < CONFIG.speed) return;
        lastDraw = timestamp;

        // 1. Re-acquire canvas every frame to handle React/Reflex re-mounts
        const currentCanvas = document.getElementById('matrix-canvas');

        if (!currentCanvas) {
            // Canvas gone (page nav?), just wait
            canvas = null;
            return;
        }

        // If canvas changed (re-mounted), re-init
        if (currentCanvas !== canvas) {
            init(currentCanvas);
        }

        if (!ctx) return;

        // Drawing
        try {
            ctx.fillStyle = CONFIG.bg;
            ctx.fillRect(0, 0, width, height);

            ctx.fillStyle = CONFIG.color;
            ctx.font = CONFIG.fontSize + 'px monospace';

            for (let i = 0; i < drops.length; i++) {
                const text = CONFIG.chars.charAt(Math.floor(Math.random() * CONFIG.chars.length));
                ctx.fillText(text, i * CONFIG.fontSize, drops[i] * CONFIG.fontSize);

                if (drops[i] * CONFIG.fontSize > height && Math.random() > 0.975) {
                    drops[i] = 0;
                }
                drops[i]++;
            }
        } catch (e) {
            console.error("MATRIX: Draw error", e);
        }
    }

    // Start Loop
    window.addEventListener('resize', resize);
    requestAnimationFrame(draw);
    console.log("MATRIX: v5 Engine Started");

})();
