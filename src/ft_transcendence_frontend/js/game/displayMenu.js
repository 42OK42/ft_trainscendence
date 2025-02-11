class MenuDisplay {
    constructor() {
        this.container = document.getElementById('menu-container');
        this.ws = new WebSocket(`ws://${window.location.hostname}:8001/ws/menu`);
        this.gameMode = null;
        this.playMode = null;
        this.currentSettings = null;  // Speichere aktuelle Einstellungen
        this.leaderboardDisplay = null;
        this.matchmakingDisplay = null;
        this.initWebSocket();
    }

    initWebSocket() {
        this.ws.onopen = () => {
            console.log('Connected to server');
            this.requestMenuItems();
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.menu_items) {
                this.displayMenuItems(data.menu_items);
                if (data.selected_mode) {
                    this.gameMode = data.selected_mode;
                }
            } else if (data.action) {
                this.handleMenuAction(data);
            }
        };
    }

    requestMenuItems() {
        this.ws.send(JSON.stringify({ action: 'get_menu_items' }));
    }

    displayMenuItems(menuItems) {
        this.container.innerHTML = '';
        menuItems.forEach(item => {
            const button = document.createElement('button');
            button.className = 'menu-item';
            button.textContent = item.text;
            button.onclick = () => this.handleMenuClick(item.id);
            this.container.appendChild(button);
        });
    }

    displaySettings(settings) {
        const currentSettings = this.currentSettings || settings;
        
        this.container.innerHTML = `
            <div class="settings-container">
                <h2>Settings</h2>
                <div class="setting-item">
                    <label for="ball-speed">Ball Speed (1-10):</label>
                    <input type="number" id="ball-speed" min="1" max="10" value="${currentSettings.ball_speed}">
                </div>
                <div class="setting-item">
                    <label for="paddle-speed">Paddle Speed (1-10):</label>
                    <input type="number" id="paddle-speed" min="1" max="10" value="${currentSettings.paddle_speed}">
                </div>
                <div class="setting-item">
                    <label for="winning-score">Winning Score:</label>
                    <input type="number" id="winning-score" min="1" max="20" value="${currentSettings.winning_score}">
                </div>
                <div class="setting-item">
                    <label for="paddle-size">Paddle Size:</label>
                    <select id="paddle-size">
                        <option value="small" ${currentSettings.paddle_size === "small" ? "selected" : ""}>Small</option>
                        <option value="middle" ${currentSettings.paddle_size === "middle" ? "selected" : ""}>Middle</option>
                        <option value="big" ${currentSettings.paddle_size === "big" ? "selected" : ""}>Big</option>
                    </select>
                </div>
                <button class="menu-item" onclick="menuDisplay.saveSettings()">Save</button>
                <button class="menu-item" onclick="menuDisplay.handleMenuClick('back')">Back</button>
            </div>
        `;
    }

    async saveSettings() {
        try {
            const settings = {
                ball_speed: parseInt(document.getElementById('ball-speed').value),
                paddle_speed: parseInt(document.getElementById('paddle-speed').value),
                winning_score: parseInt(document.getElementById('winning-score').value),
                paddle_size: document.getElementById('paddle-size').value
            };
            
            console.log('Sending settings:', settings);
            
            await this.ws.send(JSON.stringify({
                action: "update_settings",
                settings: settings
            }));
        } catch (error) {
            console.error('Error saving settings:', error);
        }
    }

    handleMenuClick(action) {
        // Prüfe Login-Status für Online-Aktionen
        if ((action === 'host' || action === 'join') && !this.isUserLoggedIn()) {
            alert('Bitte logge dich ein, um online zu spielen.');
            return;
        }

        // Sende Aktion an Server
        this.ws.send(JSON.stringify({
            action: 'menu_selection',
            selection: action
        }));
    }

    handleMenuAction(data) {
        console.log("Handling menu action:", data);
        
        if (data.is_tournament) {
            this.currentSettings = { ...this.currentSettings, tournament: true };
        }
        
        switch (data.action) {
            case 'show_matchmaking_screen':
                if (!this.isUserLoggedIn()) {
                    alert('Bitte logge dich ein, um online zu spielen.');
                    return;
                }
                if (this.matchmakingDisplay) {
                    this.matchmakingDisplay.cleanup();
                }
                this.matchmakingDisplay = window.matchmakingDisplay;
                this.matchmakingDisplay.displayMatchmakingScreen();
                break;
            case 'show_host_screen':
                if (this.matchmakingDisplay) {
                    this.matchmakingDisplay.cleanup();
                }
                this.matchmakingDisplay = window.matchmakingDisplay;
                this.matchmakingDisplay.displayHostScreen();
                break;
            case 'show_join_screen':
                if (this.matchmakingDisplay) {
                    this.matchmakingDisplay.cleanup();
                }
                this.matchmakingDisplay = window.matchmakingDisplay;
                this.matchmakingDisplay.displayJoinScreen();
                break;
            case 'show_player_names':
                this.displayPlayerNamesInput(data.num_players, this.currentSettings?.tournament);
                break;
            case 'show_main_menu':
                this.displayMenuItems(data.menu_items);
                break;
            case 'start_game':
                if (!data.is_online) {
                    this.startGame(data);
                }
                break;
            case 'show_settings':
                this.currentSettings = data.settings;  // Speichere die Einstellungen
                this.displaySettings(data.settings);
                break;
            case 'settings_updated':
                this.currentSettings = data.settings;  // Update gespeicherte Einstellungen
                alert('Settings saved successfully!');
                this.handleMenuClick('back');
                break;
            case 'settings_error':
                alert(data.message);
                break;
            case 'show_leaderboard':
                if (this.leaderboardDisplay) {
                    this.leaderboardDisplay.cleanup();
                }
                this.leaderboardDisplay = new LeaderboardDisplay();
                this.leaderboardDisplay.display();
                break;
            case 'exit_game':
                console.log('Exiting game...');
                break;
        }
    }

    displayPlayerNamesInput(numPlayers, isTournament) {
        this.container.innerHTML = `
            <div class="settings-container">
                <h2>${isTournament ? 'Tournament' : 'Game'} Players</h2>
                <form id="player-names-form">
                    ${Array.from({length: numPlayers}, (_, i) => `
                        <div class="setting-item">
                            <label for="player-${i+1}">Player ${i+1} Name:</label>
                            <input type="text" id="player-${i+1}" 
                                   value="${this.isAIPlayer(i) ? `Bot ${i+1}` : `Player ${i+1}`}"
                                   ${this.isAIPlayer(i) ? 'readonly' : ''}>
                        </div>
                    `).join('')}
                    <button type="submit" class="menu-item">Start ${isTournament ? 'Tournament' : 'Game'}</button>
                    <button type="button" class="menu-item" onclick="menuDisplay.handleMenuClick('back')">Back</button>
                </form>
            </div>
        `;

        document.getElementById('player-names-form').onsubmit = (e) => {
            e.preventDefault();
            const playerNames = Array.from({length: numPlayers}, (_, i) => 
                document.getElementById(`player-${i+1}`).value
            );
            this.startGameWithPlayers(playerNames, isTournament);
        };
    }

    isAIPlayer(index) {
        // Prüft ob der aktuelle Spieler ein Bot sein soll
        return this.currentSettings?.mode === 'ai' && index > 0;
    }

    startGameWithPlayers(playerNames, isTournament) {
        const gameSettings = this.currentSettings || {};
        gameSettings.playerNames = playerNames;
        gameSettings.isTournament = isTournament;
        
        this.ws.send(JSON.stringify({
            action: 'start_game',
            settings: gameSettings
        }));
    }

    startGame(data) {
        // Verstecke das Menü
        this.container.style.display = 'none';
        
        // Erstelle und starte das Spiel
        const gameContainer = document.getElementById('game-container');
        gameContainer.style.display = 'block';
        
        const onBackToMenu = () => {
            gameContainer.style.display = 'none';
            this.container.style.display = 'block';
            this.requestMenuItems();
        };

        window.gameScreen = new GameScreen({
            player1: { name: "Player 1", score: 0, paddle: 0 },
            player2: { name: "Player 2", score: 0, paddle: 0 },
            ball: [0, 0]
        }, onBackToMenu);
        
        window.gameScreen.display();
    }

    display() {
        this.container.innerHTML = `
            <div class="menu">
                <h1>Pong Game</h1>
                <button class="menu-item" onclick="menuDisplay.handleMenuClick('play')">Spielen</button>
                <button class="menu-item" onclick="menuDisplay.handleMenuClick('leaderboard')">Leaderboard</button>
                <button class="menu-item" onclick="menuDisplay.handleMenuClick('logout')">Logout</button>
            </div>
        `;
    }

    isUserLoggedIn() {
        // Prüfe ob ein Access Token existiert
        return localStorage.getItem('accessToken') !== null;
    }
}

const menuDisplay = new MenuDisplay(); 