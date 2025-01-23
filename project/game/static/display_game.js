class Game {
	constructor(config = null) {
		this.canvas = document.getElementById('pongCanvas');
		this.ctx = this.canvas.getContext('2d');
		this.canvas.style.display = 'block';
		
		// Warte auf Konfiguration vom Menü
		if (!config) {
			console.log("No config provided, waiting for menu selection");
			return;
		}
		
		this.withAI = config.withAI;
		this.aiDifficulty = config.difficulty;
		
		console.log("Starting game with config:", config);
		
		this.setupWebSocket();
		this.setupControls();
		this.setupPlayAgainButton();
		this.gameLoop();
	}

	setupWebSocket() {
		this.ws = new WebSocket('ws://' + window.location.hostname + ':8000/ws/game1');
		
		this.ws.onopen = () => {
			console.log("WebSocket connected, sending config");
			this.ws.send(JSON.stringify({
				withAI: this.withAI,
				difficulty: this.aiDifficulty
			}));
		};
		
		this.socket = new WebSocket('ws://localhost:8000/ws/game/');
		
		this.socket.onmessage = (event) => {
			const data = JSON.parse(event.data);
			if (data.type === 'ai_move') {
				this.player2.y = data.paddle_y;
			}
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
		this.menuBtn = document.createElement('button');
		this.menuBtn.innerText = 'Back to Menu';
		this.menuBtn.style.position = 'absolute';
		this.menuBtn.style.left = '50%';
		this.menuBtn.style.top = '60%';
		this.menuBtn.style.transform = 'translate(-50%, -50%)';
		this.menuBtn.style.padding = '10px 20px';
		this.menuBtn.style.fontSize = '20px';
		this.menuBtn.style.cursor = 'pointer';
		this.menuBtn.style.display = 'none';
		
		this.menuBtn.addEventListener('click', () => {
			// Entferne den Button
			this.menuBtn.style.display = 'none';
			
			// Cleanup
			if (this.ws) {
				this.ws.close();
			}
			
			// Verstecke das Spiel-Canvas
			this.canvas.style.display = 'none';
			
			// Starte neues Menü
			window.location.reload();
		});
		
		document.body.appendChild(this.menuBtn);
	}

	gameLoop() {
		// Clear canvas
		this.ctx.fillStyle = 'black';
		this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
		
		// Draw center line
		this.drawCenterLine();
		
		// Draw scores
		this.drawScores();
		
		// Draw players if they exist
		if (this.player1) this.drawPlayer(this.player1);
		if (this.player2) this.drawPlayer(this.player2);
		
		// Draw ball if game is not over
		if (this.ball && !this.game_over) {
			this.ctx.beginPath();
			this.ctx.arc(this.ball.x, this.ball.y, this.ball.radius, 0, Math.PI * 2);
			this.ctx.fillStyle = 'white';
			this.ctx.fill();
			this.ctx.closePath();
		}

		// Draw game over message and show menu button
		if (this.game_over && this.winner) {
			this.ctx.fillStyle = 'white';
			this.ctx.font = '48px Arial';
			this.ctx.textAlign = 'center';
			this.ctx.fillText(`${this.winner} wins!`, this.canvas.width/2, this.canvas.height/2);
			this.menuBtn.style.display = 'block';
		}
		
		requestAnimationFrame(() => this.gameLoop());
	}

	drawPlayer(player) {
		this.ctx.fillStyle = 'white';
		this.ctx.fillRect(player.x, player.y, player.width, player.height);
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

	drawScores() {
		this.ctx.fillStyle = 'white';
		this.ctx.font = '32px Arial';
		this.ctx.textAlign = 'center';
		
		// Scores direkt aus den Player-Objekten lesen
		if (this.player1 && this.player2) {
			this.ctx.fillText(this.player1.score.toString(), 100, 50);
			this.ctx.fillText(this.player2.score.toString(), 700, 50);
		}
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

	cleanup() {
		if (this.menuBtn) {
			this.menuBtn.remove();
		}
		if (this.ws) {
			this.ws.close();
		}
	}

	updateGameState(state) {
		// Debug-Ausgabe hinzufügen
		console.log('Received state update:', state);
		
		this.gameState = state;
		if (state.players && state.players.length >= 2) {
			this.player1 = state.players[0];
			this.player2 = state.players[1];
		}
	}
}

// Menü-Handler
window.onload = () => {
	const gameCanvas = document.getElementById('pongCanvas');
	if (gameCanvas) {
		gameCanvas.style.display = 'block';
		new Menu();
	}
};

// Diese Funktion wird vom Menü aufgerufen
function startGame(config) {
	console.log("Starting game with config from menu:", config);
	new Game(config);
}
