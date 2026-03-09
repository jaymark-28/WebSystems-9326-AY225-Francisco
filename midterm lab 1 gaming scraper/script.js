// script.js - Nintendo Game Hub 2026
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎮 Nintendo Game Hub initializing...');
    
    // ========== DOM Elements ==========
    const gamesGrid = document.getElementById('gamesGrid');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const totalGamesSpan = document.getElementById('totalGames');
    const switch1CountSpan = document.getElementById('switch1Count');
    const switch2CountSpan = document.getElementById('switch2Count');
    const updateDateSpan = document.getElementById('updateDate');
    const marchCountSpan = document.getElementById('marchCount');
    const upcomingCountSpan = document.getElementById('upcomingCount');
    const exclusiveCountSpan = document.getElementById('exclusiveCount');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const sortSelect = document.getElementById('sortSelect');
    const viewBtns = document.querySelectorAll('.view-btn');
    const comingSoonGrid = document.getElementById('comingSoonGrid');
    
    // ========== State ==========
    let gamesData = [];
    let currentFilter = 'all';
    let currentSearch = '';
    let currentSort = 'title';
    let currentView = 'grid';
    
    // ========== Load Games ==========
    async function loadGames() {
        try {
            const response = await fetch('games.json');
            if (!response.ok) throw new Error('Failed to load games.json');
            gamesData = await response.json();
            
            console.log(`✅ Loaded ${gamesData.length} games`);
            
            // Update stats
            updateStats();
            
            // Display games
            displayGames();
            
            // Populate coming soon
            populateComingSoon();
            
        } catch (error) {
            console.error('❌ Error:', error);
            gamesGrid.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Failed to Load Game Data</h3>
                    <p>Please make sure games.json exists in the same folder</p>
                </div>
            `;
        }
    }
    
    // ========== Update Statistics ==========
    function updateStats() {
        // Total games
        totalGamesSpan.textContent = gamesData.length;
        
        // Switch 1 games (original Switch)
        const switch1Games = gamesData.filter(g => 
            g.platform_availability.includes('Switch') && 
            !g.platform_availability.includes('Switch 2')
        );
        switch1CountSpan.textContent = switch1Games.length;
        
        // Switch 2 games
        const switch2Games = gamesData.filter(g => 
            g.platform_availability.includes('Switch 2')
        );
        switch2CountSpan.textContent = switch2Games.length;
        
        // March 2026 releases
        const marchGames = gamesData.filter(g => 
            g.release_date.includes('March')
        );
        marchCountSpan.textContent = marchGames.length;
        
        // Upcoming games (April+ or contains 2026/Summer)
        const upcomingGames = gamesData.filter(g => 
            g.release_date.includes('April') ||
            g.release_date.includes('May') ||
            g.release_date.includes('June') ||
            g.release_date.includes('July') ||
            g.release_date.includes('August') ||
            g.release_date.includes('September') ||
            g.release_date.includes('Summer') ||
            g.release_date.includes('2026') ||
            g.release_date.includes('2027')
        );
        upcomingCountSpan.textContent = upcomingGames.length;
        
        // Switch 2 exclusives
        const exclusives = gamesData.filter(g => 
            g.platform_availability.includes('Switch 2') && 
            !g.platform_availability.includes('Switch')
        );
        exclusiveCountSpan.textContent = exclusives.length;
        
        // Update date
        const now = new Date();
        updateDateSpan.textContent = now.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: 'numeric'
        });
    }
    
    // ========== Filter Games ==========
    function filterGames() {
        return gamesData.filter(game => {
            // Platform filter
            let matchesPlatform = true;
            if (currentFilter === 'switch1') {
                matchesPlatform = game.platform_availability.includes('Switch') && 
                                 !game.platform_availability.includes('Switch 2');
            } else if (currentFilter === 'switch2') {
                matchesPlatform = game.platform_availability.includes('Switch 2');
            }
            
            // Search filter
            const searchLower = currentSearch.toLowerCase();
            const matchesSearch = currentSearch === '' || 
                game.game_title.toLowerCase().includes(searchLower) ||
                game.developer.toLowerCase().includes(searchLower) ||
                game.publisher.toLowerCase().includes(searchLower) ||
                (game.genre && game.genre.toLowerCase().includes(searchLower));
            
            return matchesPlatform && matchesSearch;
        });
    }
    
    // ========== Sort Games ==========
    function sortGames(games) {
        const sorted = [...games];
        
        switch(currentSort) {
            case 'title':
                sorted.sort((a, b) => a.game_title.localeCompare(b.game_title));
                break;
            case 'date-desc':
                sorted.sort((a, b) => {
                    const dateA = parseDate(a.release_date);
                    const dateB = parseDate(b.release_date);
                    return dateB - dateA;
                });
                break;
            case 'date-asc':
                sorted.sort((a, b) => {
                    const dateA = parseDate(a.release_date);
                    const dateB = parseDate(b.release_date);
                    return dateA - dateB;
                });
                break;
        }
        
        return sorted;
    }
    
    // Helper to parse dates
    function parseDate(dateStr) {
        if (dateStr.includes('March')) return new Date(2026, 2, 1);
        if (dateStr.includes('April')) return new Date(2026, 3, 1);
        if (dateStr.includes('May')) return new Date(2026, 4, 1);
        if (dateStr.includes('June')) return new Date(2026, 5, 1);
        if (dateStr.includes('July')) return new Date(2026, 6, 1);
        if (dateStr.includes('August')) return new Date(2026, 7, 1);
        if (dateStr.includes('September')) return new Date(2026, 8, 1);
        if (dateStr.includes('Summer')) return new Date(2026, 5, 1);
        if (dateStr.includes('2027')) return new Date(2027, 0, 1);
        return new Date(2026, 0, 1);
    }
    
    // ========== Display Games ==========
    function displayGames() {
        let filtered = filterGames();
        filtered = sortGames(filtered);
        
        if (filtered.length === 0) {
            gamesGrid.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search"></i>
                    <h3>No Games Found</h3>
                    <p>Try adjusting your search or filter</p>
                </div>
            `;
            return;
        }
        
        // Apply view mode
        if (currentView === 'grid') {
            gamesGrid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(350px, 1fr))';
        } else {
            gamesGrid.style.gridTemplateColumns = '1fr';
        }
        
        gamesGrid.innerHTML = filtered.map((game, index) => createGameCard(game, index)).join('');
    }
    
    // ========== Create Game Card ==========
    function createGameCard(game, index) {
        const isSwitch2 = game.platform_availability.includes('Switch 2');
        const cardClass = isSwitch2 ? 'game-card switch2-card' : 'game-card';
        
        // Determine platform class for badge
        const platformClass = isSwitch2 ? 'switch2' : 'switch1';
        
        // Handle image
        const imageHtml = game.image_url 
            ? `<img src="${game.image_url}" alt="${escapeHtml(game.game_title)}" class="game-image" onerror="this.src='https://via.placeholder.com/300x200?text=Nintendo+Game';">`
            : `<div class="image-placeholder"><i class="fas fa-gamepad"></i></div>`;
        
        // Format features
        const featuresList = Array.isArray(game.key_features) && game.key_features[0] !== 'Not Available'
            ? game.key_features.slice(0, 3).map(f => 
                `<li><i class="fas fa-check-circle"></i> ${escapeHtml(f)}</li>`
              ).join('')
            : '<li class="not-available">No features listed</li>';
        
        return `
            <div class="${cardClass}" style="animation-delay: ${index * 0.05}s">
                <div class="game-image-container">
                    ${imageHtml}
                    <span class="platform-badge ${platformClass}">
                        <i class="fas ${isSwitch2 ? 'fa-star' : 'fa-gamepad'}"></i> 
                        ${escapeHtml(game.platform_availability)}
                    </span>
                </div>
                <div class="game-card-header">
                    <h2>${escapeHtml(game.game_title)}</h2>
                    <div class="game-meta">
                        <span><i class="fas fa-calendar-alt"></i> ${escapeHtml(game.release_date)}</span>
                        ${game.rating ? `<span><i class="fas fa-star"></i> ${escapeHtml(game.rating)}</span>` : ''}
                    </div>
                </div>
                <div class="game-card-body">
                    <div class="info-row">
                        <span class="info-label"><i class="fas fa-code-branch"></i> DEVELOPER</span>
                        <span class="info-value">${escapeHtml(game.developer)}</span>
                    </div>
                    
                    <div class="info-row">
                        <span class="info-label"><i class="fas fa-building"></i> PUBLISHER</span>
                        <span class="info-value">${escapeHtml(game.publisher)}</span>
                    </div>
                    
                    <div class="info-row">
                        <span class="info-label"><i class="fas fa-star"></i> KEY FEATURES</span>
                        <ul class="features-list">
                            ${featuresList}
                        </ul>
                    </div>
                    
                    ${game.genre ? `
                    <div class="info-row">
                        <span class="info-label"><i class="fas fa-tag"></i> GENRE</span>
                        <span class="info-value">${escapeHtml(game.genre)}</span>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    // ========== Populate Coming Soon ==========
    function populateComingSoon() {
        const upcoming = gamesData
            .filter(g => 
                g.release_date.includes('April') ||
                g.release_date.includes('May') ||
                g.release_date.includes('June') ||
                g.release_date.includes('July') ||
                g.release_date.includes('August') ||
                g.release_date.includes('September') ||
                g.release_date.includes('Summer') ||
                g.release_date.includes('2026')
            )
            .slice(0, 8);
        
        comingSoonGrid.innerHTML = upcoming.map(game => {
            const isSwitch2 = game.platform_availability.includes('Switch 2');
            return `
                <div class="coming-soon-card ${isSwitch2 ? 'switch2' : ''}">
                    <h3>${escapeHtml(game.game_title)}</h3>
                    <div class="release-date">${escapeHtml(game.release_date)}</div>
                    <div class="platform">${escapeHtml(game.platform_availability)}</div>
                </div>
            `;
        }).join('');
    }
    
    // ========== Escape HTML ==========
    function escapeHtml(text) {
        if (!text) return 'Not Available';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // ========== Event Listeners ==========
    
    // Search input
    searchInput.addEventListener('input', (e) => {
        currentSearch = e.target.value.toLowerCase();
        displayGames();
    });
    
    // Search button
    searchBtn.addEventListener('click', () => {
        currentSearch = searchInput.value.toLowerCase();
        displayGames();
    });
    
    // Enter key in search
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            currentSearch = searchInput.value.toLowerCase();
            displayGames();
        }
    });
    
    // Filter buttons
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            displayGames();
        });
    });
    
    // Sort select
    sortSelect.addEventListener('change', (e) => {
        currentSort = e.target.value;
        displayGames();
    });
    
    // View buttons
    viewBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            viewBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentView = btn.dataset.view;
            displayGames();
        });
    });
    
    // ========== Initialize ==========
    loadGames();
    
    console.log('✅ Nintendo Game Hub ready!');
});