class Game {
	constructor(withAI = false, difficulty = 0) {
		this.canvas = document.getElementById('pongCanvas');
		this.canvas.style.display = 'block';
		this.ctx = this.canvas.getContext('2d');
		console.log("Canvas initialized");
		this.ws = new WebSocket('ws://' + window.location.hostname + ':8000/ws/game1');
		
		// Set canvas size explicitly
		this.canvas.width = 800;
		this.canvas.height = 500;
		
		this.withAI = withAI;
		this.aiDifficulty = difficulty;
		
		console.log("Game initialized with:", { withAI, difficulty });  // Debug log
		
		this.setupWebSocket();
		this.setupControls();
		this.gameLoop();
		this.game_over = false;
		this.winner = null;
		this.setupPlayAgainButton();
	}

	setupWebSocket() {
		this.socket = new WebSocket('ws://localhost:8000/ws/game/');
		
		this.socket.onmessage = (event) => {
			const data = JSON.parse(event.data);
			if (data.type === 'ai_move') {
				this.player2.y = data.paddle_y;
			}
		};
		
		this.ws.onopen = () => {
			console.log('WebSocket connection established');
			this.ws.send(JSON.stringify({
				withAI: this.withAI,
				difficulty: this.aiDifficulty
			}));
		};

		this.ws.onmessage = (event) => {
			const gameState = JSON.parse(event.data);
			this.player1 = gameState.player1;
			this.player2 = gameState.player2;
			this.ball = gameState.ball;
			this.game_over = gameState.game_over;
			this.winner = gameState.winner;
		};

		this.ws.onerror = (error) => {
			console.error('WebSocket error:', error);
		};
	}

	setupControls() {
		document.addEventListener('keydown', (e) => {
			let data = null;
			
			// Wenn AI aktiv ist, ignoriere Eingaben für Spieler 2
			if (this.withAI && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
				return;
			}
			
			switch(e.key) {
				// Spieler 1 (W/S)
				case 'w':
					data = { player: 1, move: true, direction: -1 };
					break;
				case 's':
					data = { player: 1, move: true, direction: 1 };
					break;
				
				// Spieler 2 (Pfeiltasten)
				case 'ArrowUp':
					data = { player: 2, move: true, direction: -1 };
					break;
				case 'ArrowDown':
					data = { player: 2, move: true, direction: 1 };
					break;
			}
			
			if (data && this.ws.readyState === WebSocket.OPEN) {
				console.log("Sending input:", data);  // Debug log
				this.ws.send(JSON.stringify(data));
			}
		});
	}

	setupPlayAgainButton() {
		// Erstelle den Button, aber verstecke ihn zunächst
		this.playAgainBtn = document.createElement('button');
		this.playAgainBtn.innerText = 'Play Again';
		this.playAgainBtn.style.position = 'absolute';
		this.playAgainBtn.style.left = '50%';
		this.playAgainBtn.style.top = '60%';
		this.playAgainBtn.style.transform = 'translate(-50%, -50%)';
		this.playAgainBtn.style.padding = '10px 20px';
		this.playAgainBtn.style.fontSize = '20px';
		this.playAgainBtn.style.cursor = 'pointer';
		this.playAgainBtn.style.display = 'none';
		
		// Event Listener für den Button
		this.playAgainBtn.addEventListener('click', () => {
			// Entferne den Button
			this.playAgainBtn.style.display = 'none';
			
			// Starte ein neues Spiel mit den gleichen Einstellungen
			new Game(this.withAI, this.aiDifficulty);
		});
		
		document.body.appendChild(this.playAgainBtn);
	}

	gameLoop() {
		// Clear canvas
		this.ctx.fillStyle = 'black';
		this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
		
		// Draw players
		if (this.player1) this.drawPlayer(this.player1);
		if (this.player2) this.drawPlayer(this.player2);
		
		// Draw center line
		this.drawCenterLine();

		// Draw ball if game is not over
		if (this.ball && !this.game_over) {
			this.ctx.beginPath();
			this.ctx.arc(this.ball.x, this.ball.y, this.ball.radius, 0, Math.PI * 2);
			this.ctx.fillStyle = 'white';
			this.ctx.fill();
			this.ctx.closePath();
		}

		// Draw game over message and show play again button
		if (this.game_over && this.winner) {
			this.ctx.fillStyle = 'white';
			this.ctx.font = '48px Arial';
			this.ctx.textAlign = 'center';
			this.ctx.fillText(`${this.winner} wins!`, this.canvas.width/2, this.canvas.height/2);
			
			// Zeige den Play Again Button
			this.playAgainBtn.style.display = 'block';
		}
		
		requestAnimationFrame(() => this.gameLoop());
	}

	drawPlayer(player) {
		this.ctx.fillStyle = 'white';
		this.ctx.fillRect(player.x, player.y, player.width, player.height);
		
		// Draw score
		this.ctx.font = '24px Arial';
		this.ctx.fillStyle = 'white';
		this.ctx.fillText(player.score, player.is_left_player ? 100 : 700, 50);
	}

	drawCenterLine() {
		this.ctx.setLineDash([5, 15]);
		this.ctx.beginPath();
		this.ctx.moveTo(this.canvas.width / 2, 0);
		this.ctx.lineTo(this.canvas.width / 2, this.canvas.height);
		this.ctx.strokeStyle = 'white';
		this.ctx.stroke();
		this.ctx.setLineDash([]);
	}

	update() {
		// AI control for right paddle
		if (this.withAI) {
			this.updateAI();
		}

		// Wenn AI aktiviert ist, sende Ball-Position ans Backend
		if (this.withAI) {
			this.socket.send(JSON.stringify({
				type: 'update_ai',
				ball: {
					x: this.ball.x,
					y: this.ball.y,
					dx: this.ball.dx,
					dy: this.ball.dy
				},
				paddle: {
					x: this.player2.x,
					y: this.player2.y,
					height: this.player2.height
				},
				canvas_height: this.canvas.height,
				difficulty: this.aiDifficulty
			}));
		}
	}

	updateAI() {
		const paddleCenter = this.player2.y + this.player2.height / 2;
		const ballY = this.ball.y;
		let speed;

		// Speed based on difficulty
		switch(this.aiDifficulty) {
			case 0: // Easy
				speed = 3;
				break;
			case 1: // Medium
				speed = 5;
				break;
			case 2: // Hard
				speed = 7;
				break;
		}

		// Delayed reaction for easier difficulties
		if (Math.abs(paddleCenter - ballY) > speed) {
			if (paddleCenter < ballY) {
				this.player2.y += speed;
			} else {
				this.player2.y -= speed;
			}
		}
	}

	// Wenn das Spiel beendet wird (z.B. bei Verbindungsabbruch oder Neustart)
	cleanup() {
		if (this.playAgainBtn) {
			this.playAgainBtn.remove();
		}
	}
}

// Start menu
const menu = new Menu();
