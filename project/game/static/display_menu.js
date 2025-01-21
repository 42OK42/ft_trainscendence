class Menu {
    constructor() {
        this.canvas = document.getElementById('pongCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = 800;
        this.canvas.height = 600;
        
        this.setupWebSocket();
        this.setupControls();
    }

    setupWebSocket() {
        this.ws = new WebSocket('ws://localhost:8000/ws/menu');
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'menu_update') {
                this.renderMenu(data.state);
            } else if (data.type === 'start_game') {
                this.startGame(data.config);
            }
        };
    }

    setupControls() {
        document.addEventListener('keydown', (e) => {
            if (this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ key: e.key }));
            }
        });
    }

    startGame(config) {
        this.canvas.style.display = 'none';
        new Game(config.withAI, config.difficulty);
    }

    renderMenu(state) {
        // Clear background
        this.ctx.fillStyle = 'black';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Title
        this.ctx.fillStyle = 'white';
        this.ctx.font = '48px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('PONG', this.canvas.width/2, 150);

        if (state.current_state === 'main') {
            this.renderMainMenu(state);
        } else {
            this.renderDifficultyMenu(state);
        }
    }

    renderMainMenu(state) {
        this.ctx.font = '24px Arial';
        
        // Local game option
        this.ctx.fillStyle = state.selected_option === 0 ? '#00ff00' : 'white';
        this.ctx.fillText('Local Game', this.canvas.width/2, this.canvas.height/2);

        // AI game option
        this.ctx.fillStyle = state.selected_option === 1 ? '#00ff00' : 'white';
        this.ctx.fillText('Play vs AI', this.canvas.width/2, this.canvas.height/2 + 50);
    }

    renderDifficultyMenu(state) {
        this.ctx.font = '24px Arial';
        
        this.ctx.fillStyle = 'white';
        this.ctx.fillText('Select Difficulty:', this.canvas.width/2, this.canvas.height/2 - 50);

        state.difficulties.forEach((diff, index) => {
            this.ctx.fillStyle = state.selected_difficulty === index ? '#00ff00' : 'white';
            this.ctx.fillText(diff, this.canvas.width/2, this.canvas.height/2 + (index * 40));
        });
    }
}

// Start menu when page loads
window.onload = () => new Menu();