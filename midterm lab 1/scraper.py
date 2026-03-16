"""
NINTENDO GAME SCRAPER - Complete 3-File Solution
"""

from flask import Flask, jsonify, send_file, request
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

app = Flask(__name__)

class NintendoScraper:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    
    def scrape_from_url(self, custom_url):
        """Scrape games from custom URL"""
        scraped_games = []
        try:
            print(f"🕷️ Scraping URL: {custom_url}")
            response = requests.get(custom_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                if len(scraped_games) >= 15:
                    break
                    
                href = link.get('href', '')
                title = link.get_text().strip()
                title = ' '.join(title.split())
                
                if '/products/' in href and len(title) > 5:
                    skip_words = ['shop', 'cart', 'sign in', 'wishlist', 'search', 'menu']
                    if not any(word in title.lower() for word in skip_words):
                        
                        if href.startswith('http'):
                            full_url = href
                        else:
                            full_url = 'https://www.nintendo.com' + href
                        
                        developer = 'Nintendo'
                        if 'pokémon' in title.lower() or 'pokemon' in title.lower():
                            developer = 'Game Freak'
                        elif 'zelda' in title.lower() or 'mario' in title.lower():
                            developer = 'Nintendo EPD'
                        elif 'kirby' in title.lower():
                            developer = 'HAL Laboratory'
                        elif 'metroid' in title.lower():
                            developer = 'MercurySteam'
                        elif 'fire emblem' in title.lower():
                            developer = 'Intelligent Systems'
                        
                        game = {
                            'title': title,
                            'url': full_url,
                            'platform': 'Nintendo Switch',
                            'release_date': 'Check Nintendo Store',
                            'developer': developer,
                            'publisher': 'Nintendo'
                        }
                        
                        if not any(g['title'] == title for g in scraped_games):
                            scraped_games.append(game)
                            print(f"  ✓ Found: {title[:50]}...")
                            
        except Exception as e:
            print(f"Error scraping: {e}")
        
        return scraped_games
    
    def save_to_json(self, games, filename='games.json'):
        """Save games to JSON file"""
        data = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_games': len(games),
            'games': games
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(games)} games to {filename}")
        return filename

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/api/scrape', methods=['POST'])
def scrape():
    """Scrape games from custom URL and save to JSON"""
    data = request.json
    custom_url = data.get('url', '')
    
    if not custom_url:
        return jsonify({
            'success': False,
            'message': 'Please provide a URL'
        })
    
    scraper = NintendoScraper()
    
    scraped = scraper.scrape_from_url(custom_url)
    
    if len(scraped) >= 5:
        scraper.save_to_json(scraped)
        
        return jsonify({
            'success': True,
            'message': f'Successfully scraped {len(scraped)} games!',
            'games': scraped
        })
    else:
        print("⚠️ Not enough games found, using fallback...")
        fallback_games = get_fallback_games()
        scraper.save_to_json(fallback_games)
        
        return jsonify({
            'success': True,
            'message': f'Using {len(fallback_games)} popular Nintendo games',
            'games': fallback_games
        })

@app.route('/api/games')
def get_games():
    """Get games from JSON file if exists"""
    if os.path.exists('games.json'):
        with open('games.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify({'games': []})

def get_fallback_games():
    """Fallback popular Nintendo games"""
    return [
        {
            "title": "The Legend of Zelda: Tears of the Kingdom",
            "url": "https://www.nintendo.com/us/store/products/the-legend-of-zelda-tears-of-the-kingdom-switch/",
            "platform": "Nintendo Switch",
            "release_date": "May 12, 2023",
            "developer": "Nintendo EPD",
            "publisher": "Nintendo"
        },
        {
            "title": "Super Mario Bros. Wonder",
            "url": "https://www.nintendo.com/us/store/products/super-mario-bros-wonder-switch/",
            "platform": "Nintendo Switch",
            "release_date": "October 20, 2023",
            "developer": "Nintendo EPD",
            "publisher": "Nintendo"
        },
        {
            "title": "Pokémon Scarlet",
            "url": "https://www.nintendo.com/us/store/products/pokemon-scarlet-switch/",
            "platform": "Nintendo Switch",
            "release_date": "November 18, 2022",
            "developer": "Game Freak",
            "publisher": "Nintendo"
        },
        {
            "title": "Pokémon Violet",
            "url": "https://www.nintendo.com/us/store/products/pokemon-violet-switch/",
            "platform": "Nintendo Switch",
            "release_date": "November 18, 2022",
            "developer": "Game Freak",
            "publisher": "Nintendo"
        },
        {
            "title": "Mario Kart 8 Deluxe",
            "url": "https://www.nintendo.com/us/store/products/mario-kart-8-deluxe-switch/",
            "platform": "Nintendo Switch",
            "release_date": "April 28, 2017",
            "developer": "Nintendo EAD",
            "publisher": "Nintendo"
        },
        {
            "title": "Animal Crossing: New Horizons",
            "url": "https://www.nintendo.com/us/store/products/animal-crossing-new-horizons-switch/",
            "platform": "Nintendo Switch",
            "release_date": "March 20, 2020",
            "developer": "Nintendo EPD",
            "publisher": "Nintendo"
        },
        {
            "title": "Super Smash Bros. Ultimate",
            "url": "https://www.nintendo.com/us/store/products/super-smash-bros-ultimate-switch/",
            "platform": "Nintendo Switch",
            "release_date": "December 7, 2018",
            "developer": "Bandai Namco",
            "publisher": "Nintendo"
        },
        {
            "title": "Super Mario Odyssey",
            "url": "https://www.nintendo.com/us/store/products/super-mario-odyssey-switch/",
            "platform": "Nintendo Switch",
            "release_date": "October 27, 2017",
            "developer": "Nintendo EPD",
            "publisher": "Nintendo"
        },
        {
            "title": "Kirby and the Forgotten Land",
            "url": "https://www.nintendo.com/us/store/products/kirby-and-the-forgotten-land-switch/",
            "platform": "Nintendo Switch",
            "release_date": "March 25, 2022",
            "developer": "HAL Laboratory",
            "publisher": "Nintendo"
        },
        {
            "title": "Luigi's Mansion 3",
            "url": "https://www.nintendo.com/us/store/products/luigis-mansion-3-switch/",
            "platform": "Nintendo Switch",
            "release_date": "October 31, 2019",
            "developer": "Next Level Games",
            "publisher": "Nintendo"
        },
        {
            "title": "Metroid Dread",
            "url": "https://www.nintendo.com/us/store/products/metroid-dread-switch/",
            "platform": "Nintendo Switch",
            "release_date": "October 8, 2021",
            "developer": "MercurySteam",
            "publisher": "Nintendo"
        },
        {
            "title": "Splatoon 3",
            "url": "https://www.nintendo.com/us/store/products/splatoon-3-switch/",
            "platform": "Nintendo Switch",
            "release_date": "September 9, 2022",
            "developer": "Nintendo EPD",
            "publisher": "Nintendo"
        },
        {
            "title": "Xenoblade Chronicles 3",
            "url": "https://www.nintendo.com/us/store/products/xenoblade-chronicles-3-switch/",
            "platform": "Nintendo Switch",
            "release_date": "July 29, 2022",
            "developer": "Monolith Soft",
            "publisher": "Nintendo"
        },
        {
            "title": "Fire Emblem: Three Houses",
            "url": "https://www.nintendo.com/us/store/products/fire-emblem-three-houses-switch/",
            "platform": "Nintendo Switch",
            "release_date": "July 26, 2019",
            "developer": "Intelligent Systems",
            "publisher": "Nintendo"
        },
        {
            "title": "Pikmin 4",
            "url": "https://www.nintendo.com/us/store/products/pikmin-4-switch/",
            "platform": "Nintendo Switch",
            "release_date": "July 21, 2023",
            "developer": "Nintendo EPD",
            "publisher": "Nintendo"
        }
    ]

if __name__ == '__main__':
    print("="*60)
    print("🎮 NINTENDO GAME SCRAPER - COMPLETE 3 FILES")
    print("="*60)
    print("📁 Files: scraper.py + index.html + style.css")
    print("🎨 May design na!")
    print("🚀 Open: http://localhost:5000")
    print("="*60)
    app.run(debug=True, port=5000)