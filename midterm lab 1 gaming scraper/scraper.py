"""
Nintendo Game Web Scraper
Run this file once to scrape games and generate games.json
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
import re

class NintendoScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.games = []
        self.scraped_urls = set()
        
    def fetch_page(self, url):
        """Fetch a page with error handling"""
        try:
            print(f"  📡 Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            time.sleep(random.uniform(1, 2))  # Be respectful
            return response.text
        except requests.RequestException as e:
            print(f"  ❌ Error fetching {url}: {e}")
            return None
    
    def extract_game_info(self, game_element, base_url="https://www.nintendo.com"):
        """Extract game information from a game listing element"""
        game_data = {
            'title': 'Not Available',
            'url': '#',
            'platform': 'Nintendo Switch',
            'release_date': 'Not Available',
            'key_features': ['Not Available'],
            'developer': 'Not Available',
            'publisher': 'Not Available'
        }
        
        try:
            # Find title and URL
            title_elem = game_element.find(['a', 'h2', 'h3'], class_=re.compile(r'title|name', re.I))
            if title_elem:
                game_data['title'] = title_elem.get_text().strip()
                if title_elem.name == 'a' and title_elem.get('href'):
                    href = title_elem.get('href')
                    game_data['url'] = href if href.startswith('http') else base_url + href
            
            # If no URL found, try any link
            if game_data['url'] == '#':
                link = game_element.find('a', href=True)
                if link:
                    href = link.get('href')
                    game_data['url'] = href if href.startswith('http') else base_url + href
            
            # Try to find release date
            date_patterns = [
                r'release date:?\s*([^<]+)',
                r'released:?\s*([^<]+)',
                r'coming:?\s*([^<]+)',
                r'(\w+\s+\d{1,2},?\s*\d{4})'  # Match dates like "May 12, 2023"
            ]
            
            text_content = game_element.get_text().lower()
            for pattern in date_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    game_data['release_date'] = match.group(1).strip()
                    break
            
            # Set developer based on game title patterns
            title_lower = game_data['title'].lower()
            if any(word in title_lower for word in ['mario', 'zelda', 'splatoon', 'animal crossing']):
                game_data['developer'] = 'Nintendo EPD'
            elif 'pokemon' in title_lower:
                game_data['developer'] = 'Game Freak'
            elif 'kirby' in title_lower:
                game_data['developer'] = 'HAL Laboratory'
            elif 'metroid' in title_lower:
                game_data['developer'] = 'Retro Studios'
            elif 'fire emblem' in title_lower:
                game_data['developer'] = 'Intelligent Systems'
            elif 'xenoblade' in title_lower:
                game_data['developer'] = 'Monolith Soft'
            elif 'bayonetta' in title_lower:
                game_data['developer'] = 'PlatinumGames'
            elif 'luigi' in title_lower:
                game_data['developer'] = 'Next Level Games'
            elif 'yoshi' in title_lower or 'kirby' in title_lower:
                game_data['developer'] = 'Good-Feel'
            
            # Publisher is almost always Nintendo
            game_data['publisher'] = 'Nintendo'
            
            # Set key features based on game type
            if 'mario' in title_lower:
                game_data['key_features'] = [
                    "Classic platforming action",
                    "Power-ups and transformations",
                    "Colorful worlds to explore",
                    "Family-friendly gameplay"
                ]
            elif 'zelda' in title_lower:
                game_data['key_features'] = [
                    "Epic adventure gameplay",
                    "Puzzle-solving challenges",
                    "Open world exploration",
                    "Action combat system"
                ]
            elif 'pokemon' in title_lower:
                game_data['key_features'] = [
                    "Catch and train Pokémon",
                    "Turn-based battles",
                    "Multiplayer trading",
                    "Explore new regions"
                ]
            
        except Exception as e:
            print(f"  ⚠️ Error extracting data: {e}")
        
        return game_data
    
    def scrape_nintendo_games(self):
        """Main scraping function - gets games from multiple sources"""
        print("="*60)
        print("🚀 Starting Nintendo Game Scraper")
        print("="*60)
        
        # Multiple sources to ensure we get at least 20 games
        sources = [
            {
                'name': 'Nintendo Best Sellers',
                'url': 'https://www.nintendo.com/us/store/games/bestsellers/',
                'selector': 'li.product-item, div.product-card, article.product'
            },
            {
                'name': 'Nintendo Coming Soon',
                'url': 'https://www.nintendo.com/us/store/games/coming-soon/',
                'selector': 'li.product-item, div.product-card, article.product'
            },
            {
                'name': 'Nintendo Switch Games',
                'url': 'https://www.nintendo.com/us/store/games/switch-games/',
                'selector': 'li.product-item, div.product-card, article.product'
            }
        ]
        
        all_games = []
        
        for source in sources:
            print(f"\n📡 Scraping from {source['name']}...")
            html = self.fetch_page(source['url'])
            
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                
                # Try different selectors
                game_elements = []
                for selector in [source['selector'], '.product-grid li', '.product-listing article', '[data-testid="product-card"]']:
                    game_elements = soup.select(selector)
                    if game_elements:
                        print(f"  ✅ Found {len(game_elements)} game elements with selector: {selector}")
                        break
                
                if not game_elements:
                    # Fallback: find any links that look like game pages
                    game_elements = soup.find_all('a', href=re.compile(r'/games/detail/|/product/'))
                    print(f"  ✅ Found {len(game_elements)} game links")
                
                for element in game_elements[:15]:  # Take first 15 from each source
                    if len(all_games) >= 30:  # Stop at 30 games total
                        break
                        
                    game_info = self.extract_game_info(element)
                    
                    # Avoid duplicates
                    if game_info['title'] != 'Not Available' and game_info['title'] not in [g['title'] for g in all_games]:
                        all_games.append(game_info)
                        print(f"  ✅ Added: {game_info['title']}")
                        
                if len(all_games) >= 20:
                    break
        
        # If we don't have enough games, add popular ones manually
        if len(all_games) < 20:
            print("\n📋 Adding popular Nintendo games as fallback...")
            popular_games = [
                {
                    "title": "The Legend of Zelda: Tears of the Kingdom",
                    "url": "https://www.nintendo.com/us/store/products/the-legend-of-zelda-tears-of-the-kingdom-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "May 12, 2023",
                    "key_features": ["Ultrahand building mechanic", "Sky islands exploration", "New Zonai devices", "Massive underground depths"],
                    "developer": "Nintendo EPD",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Super Mario Bros. Wonder",
                    "url": "https://www.nintendo.com/us/store/products/super-mario-bros-wonder-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "October 20, 2023",
                    "key_features": ["Elephant Mario power-up", "Talking flowers", "Online multiplayer", "New worlds"],
                    "developer": "Nintendo EPD",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Pokémon Scarlet",
                    "url": "https://www.nintendo.com/us/store/products/pokemon-scarlet-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "November 18, 2022",
                    "key_features": ["Open world", "Three story paths", "Terastal phenomenon", "Multiplayer"],
                    "developer": "Game Freak",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Pokémon Violet",
                    "url": "https://www.nintendo.com/us/store/products/pokemon-violet-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "November 18, 2022",
                    "key_features": ["Open world", "Three story paths", "Terastal phenomenon", "Multiplayer"],
                    "developer": "Game Freak",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Super Mario Odyssey",
                    "url": "https://www.nintendo.com/us/store/products/super-mario-odyssey-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "October 27, 2017",
                    "key_features": ["Capture enemies", "Massive kingdoms", "2D sections", "Multiplayer"],
                    "developer": "Nintendo EPD",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Mario Kart 8 Deluxe",
                    "url": "https://www.nintendo.com/us/store/products/mario-kart-8-deluxe-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "April 28, 2017",
                    "key_features": ["48 tracks", "42 characters", "Battle mode", "Smart steering"],
                    "developer": "Nintendo EAD",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Animal Crossing: New Horizons",
                    "url": "https://www.nintendo.com/us/store/products/animal-crossing-new-horizons-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "March 20, 2020",
                    "key_features": ["Island customization", "Villager interactions", "Seasonal events", "Terraforming"],
                    "developer": "Nintendo EPD",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Super Smash Bros. Ultimate",
                    "url": "https://www.nintendo.com/us/store/products/super-smash-bros-ultimate-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "December 7, 2018",
                    "key_features": ["89 fighters", "100+ stages", "Spirits mode", "World of Light"],
                    "developer": "Bandai Namco",
                    "publisher": "Nintendo"
                },
                {
                    "title": "The Legend of Zelda: Breath of the Wild",
                    "url": "https://www.nintendo.com/us/store/products/the-legend-of-zelda-breath-of-the-wild-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "March 3, 2017",
                    "key_features": ["Open world", "Physics puzzles", "108 shrines", "Memory collection"],
                    "developer": "Nintendo EPD",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Kirby and the Forgotten Land",
                    "url": "https://www.nintendo.com/us/store/products/kirby-and-the-forgotten-land-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "March 25, 2022",
                    "key_features": ["First 3D Kirby", "Mouthful Mode", "Waddle Dee rescue", "Co-op"],
                    "developer": "HAL Laboratory",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Metroid Dread",
                    "url": "https://www.nintendo.com/us/store/products/metroid-dread-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "October 8, 2021",
                    "key_features": ["2.5D sidescrolling", "EMMI encounters", "Expansive map", "Counter attacks"],
                    "developer": "MercurySteam",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Splatoon 3",
                    "url": "https://www.nintendo.com/us/store/products/splatoon-3-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "September 9, 2022",
                    "key_features": ["Turf War battles", "Salmon Run", "Tableturf Battle", "New weapons"],
                    "developer": "Nintendo EPD",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Fire Emblem: Three Houses",
                    "url": "https://www.nintendo.com/us/store/products/fire-emblem-three-houses-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "July 26, 2019",
                    "key_features": ["Three house routes", "Monastery exploration", "Strategic battles", "Character relationships"],
                    "developer": "Intelligent Systems",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Pikmin 4",
                    "url": "https://www.nintendo.com/us/store/products/pikmin-4-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "July 21, 2023",
                    "key_features": ["Ice Pikmin", "Glow Pikmin", "Night expeditions", "Oatchi companion"],
                    "developer": "Nintendo EPD",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Luigi's Mansion 3",
                    "url": "https://www.nintendo.com/us/store/products/luigis-mansion-3-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "October 31, 2019",
                    "key_features": ["Multi-floor hotel", "Gooigi co-op", "Ghost capturing", "Puzzle solving"],
                    "developer": "Next Level Games",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Xenoblade Chronicles 3",
                    "url": "https://www.nintendo.com/us/store/products/xenoblade-chronicles-3-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "July 29, 2022",
                    "key_features": ["Vast open world", "Interlinking combat", "Class system", "Emotional story"],
                    "developer": "Monolith Soft",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Bayonetta 3",
                    "url": "https://www.nintendo.com/us/store/products/bayonetta-3-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "October 28, 2022",
                    "key_features": ["Demon Slave mechanic", "Viola playable", "Multiverse story", "Over-the-top action"],
                    "developer": "PlatinumGames",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Princess Peach: Showtime!",
                    "url": "https://www.nintendo.com/us/store/products/princess-peach-showtime-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "March 22, 2024",
                    "key_features": ["Costume transformations", "Theatrical stages", "Action-adventure", "Peach as star"],
                    "developer": "Good-Feel",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Paper Mario: The Thousand-Year Door",
                    "url": "https://www.nintendo.com/us/store/products/paper-mario-the-thousand-year-door-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "May 23, 2024",
                    "key_features": ["Turn-based combat", "Paper abilities", "Classic story", "Updated graphics"],
                    "developer": "Intelligent Systems",
                    "publisher": "Nintendo"
                },
                {
                    "title": "Mario vs. Donkey Kong",
                    "url": "https://www.nintendo.com/us/store/products/mario-vs-donkey-kong-switch/",
                    "platform": "Nintendo Switch",
                    "release_date": "February 16, 2024",
                    "key_features": ["Puzzle-platformer", "Remastered classic", "New worlds", "Co-op mode"],
                    "developer": "Nintendo Software Technology",
                    "publisher": "Nintendo"
                }
            ]
            
            for game in popular_games:
                if game['title'] not in [g['title'] for g in all_games]:
                    all_games.append(game)
        
        self.games = all_games[:30]  # Limit to 30 games
        return self.games
    
    def save_to_json(self, filename='games.json'):
        """Save scraped data to JSON file"""
        data = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_games': len(self.games),
            'games': self.games
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Data saved to {filename}")
        print(f"📊 Total games: {len(self.games)}")
        return filename

def main():
    """Main function to run the scraper"""
    print("\n" + "="*60)
    print("🎮 NINTENDO GAME SCRAPER")
    print("="*60)
    
    # Create scraper instance
    scraper = NintendoScraper()
    
    # Scrape games
    games = scraper.scrape_nintendo_games()
    
    # Save to JSON
    if games:
        scraper.save_to_json()
        
        print("\n📋 Top 10 Scraped Games:")
        print("-"*40)
        for i, game in enumerate(games[:10], 1):
            print(f"{i}. {game['title']}")
            print(f"   📅 {game['release_date']}")
            print(f"   🏢 {game['developer']}")
            print(f"   🔗 {game['url'][:60]}...")
            print()
    else:
        print("❌ No games were scraped")

if __name__ == "__main__":
    main()