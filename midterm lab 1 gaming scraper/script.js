// script.js
class GameDirectory {
    constructor() {
        this.games = [];
        this.filteredGames = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.disableControls(true);
    }

    setupEventListeners() {
        const loadBtn = document.getElementById('loadGamesBtn');
        loadBtn.addEventListener('click', () => this.loadGames());

        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', () => this.filterGames());

        const platformFilter = document.getElementById('platformFilter');
        platformFilter.addEventListener('change', () => this.filterGames());

        const sortFilter = document.getElementById('sortFilter');
        sortFilter.addEventListener('change', () => this.sortGames());
    }

    disableControls(disabled) {
        const searchInput = document.getElementById('searchInput');
        const platformFilter = document.getElementById('platformFilter');
        const sortFilter = document.getElementById('sortFilter');
        
        searchInput.disabled = disabled;
        platformFilter.disabled = disabled;
        sortFilter.disabled = disabled;
    }

    // Function to normalize text (remove accents, special characters)
    normalizeText(text) {
        if (!text) return '';
        return text
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '') // Remove accents
            .replace(/[^a-z0-9\s]/g, ''); // Remove special characters except spaces
    }

    async loadGames() {
        const loadBtn = document.getElementById('loadGamesBtn');
        const originalText = loadBtn.innerHTML;
        
        try {
            loadBtn.innerHTML = '<span class="btn-icon">⏳</span> Loading...';
            loadBtn.disabled = true;
            
            document.getElementById('gamesGrid').innerHTML = '<div class="loading">Loading games...</div>';
            
            const response = await fetch('games.json');
            
            if (!response.ok) {
                throw new Error('games.json not found. Run scraper.py first');
            }
            
            const data = await response.json();
            this.games = data.games || [];
            this.filteredGames = [...this.games];
            
            this.disableControls(false);
            
            if (data.last_updated) {
                document.getElementById('lastUpdated').textContent = 
                    `Updated: ${data.last_updated}`;
            }
            
            document.getElementById('gameCount').textContent = 
                `Showing ${this.games.length} games`;
            
            this.render();
            this.showToast(`Loaded ${this.games.length} games`, 'success');
            
        } catch (error) {
            document.getElementById('gamesGrid').innerHTML = `
                <div class="no-results">
                    <h3>No games found</h3>
                    <p>Please run: python scraper.py</p>
                </div>
            `;
            
            document.getElementById('gameCount').textContent = 
                'Run scraper.py first';
            
            this.showToast('Failed to load games', 'error');
        } finally {
            loadBtn.innerHTML = originalText;
            loadBtn.disabled = false;
        }
    }

    filterGames() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
        const platform = document.getElementById('platformFilter').value;

        // Normalize the search term (remove accents)
        const normalizedSearchTerm = this.normalizeText(searchTerm);

        console.log('Original search:', searchTerm);
        console.log('Normalized search:', normalizedSearchTerm);
        console.log('Total games:', this.games.length);

        this.filteredGames = this.games.filter(game => {
            // Get all searchable fields
            const title = game.title || '';
            const developer = game.developer || '';
            const publisher = game.publisher || '';
            
            // Create normalized versions (without accents)
            const normalizedTitle = this.normalizeText(title);
            const normalizedDeveloper = this.normalizeText(developer);
            const normalizedPublisher = this.normalizeText(publisher);

            // Check if search term is empty
            if (searchTerm === '') {
                return true;
            }

            // Check original text (for exact matches with accents)
            const matchesOriginal = 
                title.toLowerCase().includes(searchTerm) ||
                developer.toLowerCase().includes(searchTerm) ||
                publisher.toLowerCase().includes(searchTerm);

            // Check normalized text (for matches without accents)
            const matchesNormalized = 
                normalizedTitle.includes(normalizedSearchTerm) ||
                normalizedDeveloper.includes(normalizedSearchTerm) ||
                normalizedPublisher.includes(normalizedSearchTerm);

            // Platform filter
            const matchesPlatform = platform === 'all' || 
                (game.platform && game.platform.toLowerCase() === platform.toLowerCase());

            return (matchesOriginal || matchesNormalized) && matchesPlatform;
        });

        console.log('Found matches:', this.filteredGames.length);
        console.log('Matching games:', this.filteredGames.map(g => g.title));

        this.sortGames();
        
        document.getElementById('gameCount').textContent = 
            `Showing ${this.filteredGames.length} of ${this.games.length} games`;
    }

    sortGames() {
        const sortBy = document.getElementById('sortFilter').value;
        
        this.filteredGames.sort((a, b) => {
            let valueA = a[sortBy] || '';
            let valueB = b[sortBy] || '';
            
            if (sortBy === 'release_date') {
                return this.compareDates(valueA, valueB);
            }
            
            return valueA.toString().localeCompare(valueB.toString());
        });
        
        this.render();
    }

    compareDates(dateA, dateB) {
        const months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        };
        
        const parseDate = (dateStr) => {
            if (dateStr === 'Not Available' || !dateStr) return 0;
            const parts = dateStr.toLowerCase().split(' ');
            if (parts.length >= 3) {
                const month = months[parts[0]] || 0;
                const year = parseInt(parts[2]) || 0;
                return year * 12 + month;
            }
            return 0;
        };
        
        return parseDate(dateA) - parseDate(dateB);
    }

    render() {
        const grid = document.getElementById('gamesGrid');
        
        if (this.filteredGames.length === 0) {
            grid.innerHTML = '<div class="no-results">No games found</div>';
            return;
        }

        grid.innerHTML = this.filteredGames.map((game, index) => 
            this.createGameCard(game, index)
        ).join('');
        
        this.addCardClickHandlers();
    }

    createGameCard(game, index) {
        const features = Array.isArray(game.key_features) 
            ? game.key_features.slice(0, 4) 
            : ['Nintendo gameplay'];

        // Format release date nicely
        const releaseDate = game.release_date || 'TBA';
        
        return `
            <div class="game-card" 
                 data-url="${this.escapeHtml(game.url || '#')}" 
                 data-title="${this.escapeHtml(game.title)}"
                 style="animation-delay: ${index * 0.05}s">
                <div class="game-header">
                    <h2>${this.escapeHtml(game.title)}</h2>
                    <span class="game-platform">${this.escapeHtml(game.platform || 'Nintendo Switch')}</span>
                </div>
                <div class="game-body">
                    <div class="game-info">
                        <div class="info-row">
                            <span class="info-label">Released:</span>
                            <span class="info-value">${this.escapeHtml(releaseDate)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Developer:</span>
                            <span class="info-value">${this.escapeHtml(game.developer || 'Nintendo')}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Publisher:</span>
                            <span class="info-value">${this.escapeHtml(game.publisher || 'Nintendo')}</span>
                        </div>
                    </div>
                    
                    <div class="game-features">
                        <h3>Features:</h3>
                        <ul class="features-list">
                            ${features.map(f => `<li>${this.escapeHtml(f)}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }

    addCardClickHandlers() {
        const cards = document.querySelectorAll('.game-card');
        cards.forEach(card => {
            card.addEventListener('click', () => {
                const url = card.dataset.url;
                const title = card.dataset.title;
                
                if (url && url !== '#') {
                    window.open(url, '_blank');
                    this.showToast(`Opening ${title}...`, 'success');
                }
            });
        });
    }

    showToast(message, type = 'success') {
        const existingToast = document.querySelector('.toast');
        if (existingToast) existingToast.remove();

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 2000);
    }

    escapeHtml(text) {
        if (!text) return 'N/A';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new GameDirectory();
});