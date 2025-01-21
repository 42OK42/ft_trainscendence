class PongDisplay {
    constructor() {
        this.canvas = document.getElementById('pongCanvas');
        this.ctx = this.canvas.getContext('2d');
        console.log("Canvas initialized");
        this.ws = new WebSocket('ws://' + window.location.hostname + ':8000/ws/game1');
        this.setupWebSocket();
        this.setupControls();
    }

    setupWebSocket() {
        this.ws.onopen = () => {
            console.log('WebSocket connection established');
            // Send initial message
            this.ws.send(JSON.stringify({action: 'START'}));
        };

        this.ws.onmessage = (event) => {
            console.log('Data received:', event.data);
            const gameState = JSON.parse(event.data);
            this.draw(gameState);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    setupControls() {
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'w':
                    this.ws.send(JSON.stringify({action: 'PADDLE1_UP'}));
                    break;
                case 's':
                    this.ws.send(JSON.stringify({action: 'PADDLE1_DOWN'}));
                    break;
                case 'ArrowUp':
                    this.ws.send(JSON.stringify({action: 'PADDLE2_UP'}));
                    break;
                case 'ArrowDown':
                    this.ws.send(JSON.stringify({action: 'PADDLE2_DOWN'}));
                    break;
            }
        });
    }

    draw(gameState) {
        console.log('Drawing game state:', gameState);
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw ball
        this.ctx.fillStyle = 'white';
        this.ctx.beginPath();
        this.ctx.arc(gameState.ball_x, gameState.ball_y, 10, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Draw paddles
        this.ctx.fillRect(50, gameState.paddle1_y, 10, 100);
        this.ctx.fillRect(740, gameState.paddle2_y, 10, 100);

        // Draw score
        this.ctx.font = '48px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(gameState.score1 + ' - ' + gameState.score2, 400, 50);
    }
}

// Spiel starten
const game = new PongDisplay();
