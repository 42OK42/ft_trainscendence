class Menu {
    constructor() {
        this.canvas = document.getElementById('pongCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = 800;
        this.canvas.height = 600;
        
        this.menuState = 'main'; // 'main' or 'difficulty'
        this.selectedOption = 0;
        this.difficulties = ['Easy', 'Medium', 'Hard'];
        this.selectedDifficulty = 0;
        
        this.setupMenuControls();
        this.drawMenu();
    }

    setupMenuControls() {
        document.addEventListener('keydown', (e) => {
            if (this.menuState === 'main') {
                this.handleMainMenuInput(e);
            } else if (this.menuState === 'difficulty') {
                this.handleDifficultyMenuInput(e);
            }
            this.drawMenu();
        });
    }

    handleMainMenuInput(e) {
        switch(e.key) {
            case 'ArrowUp':
                this.selectedOption = 0;
                break;
            case 'ArrowDown':
                this.selectedOption = 1;
                break;
            case 'Enter':
                if (this.selectedOption === 0) {
                    // Start local game
                    this.startGame(false);
                } else {
                    // Switch to difficulty selection
                    this.menuState = 'difficulty';
                }
                break;
        }
    }

    handleDifficultyMenuInput(e) {
        switch(e.key) {
            case 'ArrowUp':
                this.selectedDifficulty = (this.selectedDifficulty - 1 + 3) % 3;
                break;
            case 'ArrowDown':
                this.selectedDifficulty = (this.selectedDifficulty + 1) % 3;
                break;
            case 'Enter':
                this.startGame(true);
                break;
            case 'Escape':
                this.menuState = 'main';
                break;
        }
    }

    startGame(withAI) {
        this.canvas.style.display = 'none';
        if (withAI) {
            new Game(true, this.selectedDifficulty);
        } else {
            new Game(false);
        }
    }

    drawMenu() {
        // Clear background
        this.ctx.fillStyle = 'black';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Title
        this.ctx.fillStyle = 'white';
        this.ctx.font = '48px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('PONG', this.canvas.width/2, 150);

        if (this.menuState === 'main') {
            this.drawMainMenu();
        } else {
            this.drawDifficultyMenu();
        }
    }

    drawMainMenu() {
        this.ctx.font = '24px Arial';
        
        // Local game option
        this.ctx.fillStyle = this.selectedOption === 0 ? '#00ff00' : 'white';
        this.ctx.fillText('Local Game', this.canvas.width/2, this.canvas.height/2);

        // AI game option
        this.ctx.fillStyle = this.selectedOption === 1 ? '#00ff00' : 'white';
        this.ctx.fillText('Play vs AI', this.canvas.width/2, this.canvas.height/2 + 50);

        // Control hints
        this.ctx.fillStyle = 'gray';
        this.ctx.font = '16px Arial';
        this.ctx.fillText('Arrow keys to select, Enter to confirm', 
            this.canvas.width/2, this.canvas.height - 50);
    }

    drawDifficultyMenu() {
        this.ctx.font = '24px Arial';
        
        this.ctx.fillStyle = 'white';
        this.ctx.fillText('Select Difficulty:', this.canvas.width/2, this.canvas.height/2 - 50);

        // Difficulty levels
        this.difficulties.forEach((diff, index) => {
            this.ctx.fillStyle = this.selectedDifficulty === index ? '#00ff00' : 'white';
            this.ctx.fillText(diff, this.canvas.width/2, this.canvas.height/2 + (index * 40));
        });

        // Control hints
        this.ctx.fillStyle = 'gray';
        this.ctx.font = '16px Arial';
        this.ctx.fillText('Arrow keys to select, Enter to confirm, ESC to go back', 
            this.canvas.width/2, this.canvas.height - 50);
    }
} 