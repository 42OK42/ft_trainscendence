class MatchmakingDisplay {
    constructor() {
        this.container = document.getElementById('menu-container');
        this.ws = null;
    }

    displayMatchmakingScreen() {
        // Zuerst WebSocket verbinden
        this.ws = new WebSocket(`ws://${window.location.hostname}:8001/ws/game/matchmaking`);
        
        this.ws.onopen = () => {
            console.log('Connected to matchmaking server');
            // Nach Verbindung den Suchscreen anzeigen
            this.container.innerHTML = `
                <div class="matchmaking-container">
                    <h2>Suche nach Spieler...</h2>
                    <div class="loading-spinner"></div>
                    <button class="menu-button" onclick="matchmakingDisplay.cancelSearch()">
                        Abbrechen
                    </button>
                </div>
            `;
            // Starte Spielersuche
            this.ws.send(JSON.stringify({
                action: 'find_game'
            }));
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Received matchmaking message:', data);
            
            switch (data.action) {
                case 'game_found':
                    this.startCountdown(data.opponent, data.game_id);
                    break;

                case 'start_game':
                    gameScreen.init(data.game_id, data.player_role);
                    break;

                case 'error':
                    alert(data.message);
                    this.cancelSearch();
                    break;
            }
        };

        this.ws.onerror = (error) => {
            console.error('Matchmaking WebSocket error:', error);
            alert('Verbindungsfehler beim Matchmaking');
            this.cancelSearch();
        };
    }

    startCountdown(opponent, gameId) {
        let countdown = 3;
        this.container.innerHTML = `
            <div class="matchmaking-container">
                <h2>Spieler gefunden!</h2>
                <p>Gegner: ${opponent}</p>
                <div class="countdown">${countdown}</div>
                <p>Spiel startet in...</p>
            </div>
        `;

        const countdownInterval = setInterval(() => {
            countdown--;
            const countdownElement = this.container.querySelector('.countdown');
            if (countdownElement) {
                countdownElement.textContent = countdown;
            }
            
            if (countdown <= 0) {
                clearInterval(countdownInterval);
            }
        }, 1000);
    }

    cancelSearch() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action: 'cancel_search'
            }));
        }
        this.cleanup();
        menuDisplay.handleMenuClick('back');
    }

    cleanup() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}

// Globale Instanz erstellen
window.matchmakingDisplay = new MatchmakingDisplay(); 