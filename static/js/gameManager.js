async function loadScript(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.body.appendChild(script);
    });
}

async function startNewGame() {
    const gameContainer = document.getElementById('game-container');
    const connectingText = document.getElementById('connecting-text');
    const countdownText = document.getElementById('countdown-text');

    // Clear the previous game content
    gameContainer.innerHTML = '';
    connectingText.textContent = 'Connecting to Game...';
    countdownText.textContent = '';

    try {
        await loadScript("https://cdnjs.cloudflare.com/ajax/libs/phaser/3.60.0/phaser.min.js");
        console.log('Phaser library loaded');

        await loadScript("static/js/phasergame.js");
        console.log('Phaser game script loaded');

        // Phaser game has been loaded and started
        console.log('Phaser game started');
        connectingText.textContent = ''; // Hide connecting text

        // Start countdown for the next game
        let countdown = 5;
        const countdownInterval = setInterval(() => {
            if (countdown >= 0) {
                countdownText.textContent = `Game starts in ${countdown} seconds`;
                countdown--;
            } else {
                countdownText.textContent = '';
                clearInterval(countdownInterval);
            }
        }, 1000);
    } catch (error) {
        console.error('Error loading scripts:', error);
    }
}

// Start a new game every 5 seconds
setInterval(startNewGame, 5000);

// Call startNewGame once when the page loads
startNewGame();
