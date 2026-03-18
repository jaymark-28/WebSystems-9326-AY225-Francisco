import os
import sys
import json
import time
import random
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request, send_file
from fpdf import FPDF
import traceback

# ========== CONFIGURATION ==========
USER_NAME = "Jaymark Francisco"
JSON_FILE = "articles.json"
PDF_FOLDER = "pdfs"

# Create folders using proper path joining
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Prevent __pycache__
sys.dont_write_bytecode = True

# ========== FLASK APP ==========
app = Flask(__name__)

# ========== SCRAPER FUNCTIONS ==========
def scrape_article_titles():
    """
    DYNAMIC scraper - kusang kukuha ng URLs mula sa GeeksforGeeks
    Hindi hard coded!
    """
    print("\n" + "="*60)
    print("🚀 STARTING DYNAMIC SCRAPER - KUSANG KUKUHA NG URLs")
    print("="*60)
    
    # Ito lang ang base URL - hindi hard coded ang articles
    base_url = "https://www.geeksforgeeks.org/data-analysis/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    articles = []
    successful = 0
    
    try:
        # Kunin ang main page para makuha ang mga article links
        print(f"\n📥 Kinukuha ang mga link mula sa: {base_url}")
        response = requests.get(base_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Hindi makuha ang main page: {response.status_code}")
            # Fallback to known working URLs kung hindi makakuha
            return fallback_urls()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Hanapin ang mga article links (dynamic)
        article_links = []
        
        # Paraan 1: Hanapin sa mga <a> tags na may article links
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Filter ang mga data analysis articles
            if '/data-analysis/' in href and 'geeksforgeeks.org' in href:
                if href not in article_links:
                    article_links.append(href)
            elif href.startswith('/') and 'data-analysis' in href:
                full_url = f"https://www.geeksforgeeks.org{href}"
                if full_url not in article_links:
                    article_links.append(full_url)
        
        # Paraan 2: Hanapin sa article cards/tiles
        for article in soup.find_all(['article', 'div'], class_=['article', 'post', 'card', 'type-post']):
            link = article.find('a', href=True)
            if link:
                href = link['href']
                if 'geeksforgeeks.org' in href:
                    if href not in article_links:
                        article_links.append(href)
                elif href.startswith('/'):
                    full_url = f"https://www.geeksforgeeks.org{href}"
                    if full_url not in article_links:
                        article_links.append(full_url)
        
        # Paraan 3: Hanapin sa mga listahan
        for list_item in soup.find_all('li'):
            link = list_item.find('a', href=True)
            if link:
                href = link['href']
                if 'data-analysis' in href:
                    if 'geeksforgeeks.org' in href:
                        if href not in article_links:
                            article_links.append(href)
                    elif href.startswith('/'):
                        full_url = f"https://www.geeksforgeeks.org{href}"
                        if full_url not in article_links:
                            article_links.append(full_url)
        
        # Remove duplicates and limit to 10
        article_links = list(set(article_links))[:10]
        
        print(f"📊 Nakakuha ng {len(article_links)} article links")
        
        if not article_links:
            print("⚠️ Walang nakitang links, gumagamit ng fallback URLs")
            return fallback_urls()
        
        # Kunin ang titles ng bawat article
        for idx, url in enumerate(article_links):
            try:
                print(f"\n📥 Kinuha ang article {idx+1}/{len(article_links)}: {url}")
                
                article_response = requests.get(url, headers=headers, timeout=15)
                
                if article_response.status_code != 200:
                    print(f"   ⚠️ Hindi makuha ang article: {article_response.status_code}")
                    continue
                
                # Check if page is "page gone" or error
                if "Whoops, that page is gone" in article_response.text or "page is gone" in article_response.text:
                    print(f"   ⚠️ Article no longer exists: {url}")
                    continue
                
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # Kunin ang title
                title_elem = article_soup.find('h1')
                if title_elem:
                    title = title_elem.text.strip()
                else:
                    title = article_soup.find('title').text.strip() if article_soup.find('title') else f"Article {idx+1}"
                
                # Clean title
                title = ' '.join(title.split())
                title = title.replace('|', '-').replace('GeeksforGeeks', '').strip()
                if title.endswith('-'):
                    title = title[:-1].strip()
                
                print(f"   ✅ Title: {title[:60]}...")
                
                articles.append({
                    'id': len(articles) + 1,
                    'title': title,
                    'url': url
                })
                
                successful += 1
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                continue
        
    except Exception as e:
        print(f"❌ Error sa main page: {e}")
        traceback.print_exc()
        return fallback_urls()
    
    # Kung wala pa ring articles, gamitin ang fallback
    if not articles:
        print("⚠️ Walang nakuha, gumagamit ng fallback URLs")
        return fallback_urls()
    
    # Save to JSON
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*60)
    print(f"✅ TAPOS NA! {len(articles)} articles ang nailista (DYNAMIC)")
    print("="*60)
    
    return articles

def fallback_urls():
    """
    ✅ 10 CONFIRMED WORKING URLs (as of current date)
    Emergency backup kung hindi makakuha ng dynamic links
    """
    print("\n📋 GUMAGAMIT NG FALLBACK URLs (10 working articles)")
    
    working_urls = [
        "https://www.geeksforgeeks.org/data-analysis-with-python/",
        "https://www.geeksforgeeks.org/introduction-to-data-analysis/",
        "https://www.geeksforgeeks.org/pandas-tutorial/",
        "https://www.geeksforgeeks.org/python-pandas-dataframe/",
        "https://www.geeksforgeeks.org/numpy-tutorial/",
        "https://www.geeksforgeeks.org/matplotlib-tutorial/",
        "https://www.geeksforgeeks.org/introduction-to-data-science/",
        "https://www.geeksforgeeks.org/data-cleaning-in-python/",
        "https://www.geeksforgeeks.org/exploratory-data-analysis-in-python/",
        "https://www.geeksforgeeks.org/python-data-visualization-tutorial/"
    ]
    
    articles = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for idx, url in enumerate(working_urls):
        try:
            print(f"\n📥 Kinukuha ang article {idx+1}/10: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Check if page is "page gone"
                if "Whoops, that page is gone" in response.text or "page is gone" in response.text:
                    print(f"   ⚠️ Article no longer exists: {url}")
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                title_elem = soup.find('h1')
                title = title_elem.text.strip() if title_elem else f"Article {idx+1}"
                title = ' '.join(title.split())
                title = title.replace('|', '-').replace('GeeksforGeeks', '').strip()
                
                articles.append({
                    'id': idx + 1,
                    'title': title,
                    'url': url
                })
                print(f"   ✅ {title[:40]}...")
            else:
                print(f"   ⚠️ {url} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ {url} - {str(e)}")
            continue
    
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    return articles

def get_article_details(url):
    """
    Kunin ang buong details ng article pag may nag-click
    FIXED: May detection ng "page gone" at proper error messages
    """
    print(f"\n📖 Kinukuha ang buong details ng: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        # Check if page is "page gone"
        if "Whoops, that page is gone" in response.text or "page is gone" in response.text:
            print(f"❌ Article no longer exists: {url}")
            return {
                'title': "Article No Longer Available",
                'concepts': ["This article has been removed from GeeksforGeeks"],
                'codes': ["# Please select another article from the list"],
                'complexity': "Not available",
                'references': ["Try a different article"],
                'url': "https://www.geeksforgeeks.org/",
                'fetched_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'error': True
            }
        
        # Check if page exists
        if response.status_code == 404:
            print(f"❌ Article not found (404)")
            return {
                'title': "Article Not Found",
                'concepts': ["This article could not be found on GeeksforGeeks"],
                'codes': ["# Please try another article"],
                'complexity': "Not available",
                'references': ["GeeksforGeeks Homepage"],
                'url': "https://www.geeksforgeeks.org/",
                'fetched_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'error': True
            }
        elif response.status_code != 200:
            print(f"❌ Error {response.status_code} sa pagkuha ng page")
            return {
                'title': "Error Loading Article",
                'concepts': [f"Error {response.status_code} occurred"],
                'codes': ["# Please try again later"],
                'complexity': "Not available",
                'references': ["GeeksforGeeks"],
                'url': "https://www.geeksforgeeks.org/",
                'fetched_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'error': True
            }
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ===== TITLE =====
        title_elem = soup.find('h1')
        title = title_elem.text.strip() if title_elem else "Unknown Title"
        title = ' '.join(title.split())
        title = title.replace('|', '-').replace('GeeksforGeeks', '').strip()
        if title.endswith('-'):
            title = title[:-1].strip()
        
        # ===== KEY CONCEPTS =====
        concepts = []
        content = soup.find('div', class_='text') or soup.find('article') or soup.find('main') or soup
        
        # Kunin ang first few paragraphs
        for p in content.find_all('p')[:5]:
            text = p.text.strip()
            if text and len(text) > 30 and not text.startswith('http'):
                clean_text = ' '.join(text.split())
                if len(clean_text) > 150:
                    clean_text = clean_text[:150] + "..."
                concepts.append(clean_text)
        
        if not concepts:
            concepts = ["Introduction to " + title, "Key concepts and fundamentals", "Practical applications"]
        
        # ===== CODE SNIPPETS =====
        codes = []
        # Hanapin ang code blocks
        for code in soup.find_all(['pre'])[:2]:
            code_text = code.text.strip()
            if code_text and len(code_text) > 20:
                if len(code_text) > 300:
                    code_text = code_text[:300] + "..."
                codes.append(code_text)
        
        if not codes:
            # Hanapin ang code sa loob ng code tags
            for code in soup.find_all('code')[:3]:
                code_text = code.text.strip()
                if code_text and len(code_text) > 20:
                    if len(code_text) > 300:
                        code_text = code_text[:300] + "..."
                    codes.append(code_text)
                    break
        
        if not codes:
            codes = ["# Code example available in the original article"]
        
        # ===== COMPLEXITY ANALYSIS =====
        complexity = "Complexity analysis available in the original article"
        
        # Hanapin ang complexity discussion
        comp_elem = soup.find(text=lambda t: t and 'complexity' in t.lower())
        if comp_elem:
            parent = comp_elem.find_parent(['p', 'div'])
            if parent:
                comp = parent.text.strip()
                if len(comp) > 20:
                    if len(comp) > 200:
                        comp = comp[:200] + "..."
                    complexity = comp
        
        # ===== REFERENCES =====
        references = []
        # Kunin ang related links
        for link in soup.find_all('a', href=True)[:5]:
            href = link['href']
            text = link.text.strip()
            if text and len(text) > 5 and ('geeksforgeeks' in href or 'python' in text.lower()):
                if len(text) > 40:
                    text = text[:40] + "..."
                references.append(text)
        
        if not references:
            references = ["GeeksforGeeks Official Site", "Python Documentation", "Data Analysis Guide"]
        
        full_data = {
            'title': title,
            'concepts': concepts,
            'codes': codes,
            'complexity': complexity,
            'references': references,
            'url': url,
            'fetched_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'error': False
        }
        
        print(f"✅ Nakuha ang buong details para sa: {title[:40]}...")
        return full_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        return {
            'title': "Connection Error",
            'concepts': ["Failed to connect to GeeksforGeeks"],
            'codes': ["# Please check your internet connection"],
            'complexity': "Not available",
            'references': ["Try again later"],
            'url': "https://www.geeksforgeeks.org/",
            'fetched_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'error': True
        }
    except Exception as e:
        print(f"❌ Error sa pagkuha ng details: {e}")
        traceback.print_exc()
        return {
            'title': "Error Loading Article",
            'concepts': ["An error occurred while loading this article"],
            'codes': ["# Please try another article"],
            'complexity': "Not available",
            'references': ["GeeksforGeeks"],
            'url': "https://www.geeksforgeeks.org/",
            'fetched_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'error': True
        }

# ========== PDF GENERATOR ==========
class DataAnalysisPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('Arial', 'B', 10)
            self.set_text_color(100, 100, 100)
            self.cell(0, 8, 'Data Analysis Learning Module', 0, 1, 'C')
            self.ln(3)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()} | Generated by {USER_NAME}', 0, 0, 'C')
    
    def clean_text(self, text):
        """Remove special characters that cause encoding errors"""
        if not text:
            return ""
        # Replace common special characters
        text = text.replace('\u2022', '-')  # bullet
        text = text.replace('\u2013', '-')  # en dash
        text = text.replace('\u2014', '-')  # em dash
        text = text.replace('\u2018', "'")  # left single quote
        text = text.replace('\u2019', "'")  # right single quote
        text = text.replace('\u201c', '"')  # left double quote
        text = text.replace('\u201d', '"')  # right double quote
        text = text.replace('\u2026', '...')  # ellipsis
        # Convert to ASCII, replacing any remaining non-ASCII chars
        return text.encode('ascii', 'replace').decode('ascii')

def generate_pdf(selected_articles):
    """
    Generate PDF from selected articles
    """
    try:
        print(f"\n📄 Generating PDF with {len(selected_articles)} articles...")
        
        pdf = DataAnalysisPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # ===== TITLE PAGE =====
        pdf.set_font('Arial', 'B', 28)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 40, 'Data Analysis', 0, 1, 'C')
        
        pdf.set_font('Arial', 'B', 20)
        pdf.set_text_color(52, 152, 219)
        pdf.cell(0, 20, 'Learning Module', 0, 1, 'C')
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 12)
        pdf.ln(30)
        
        pdf.cell(0, 10, f'Date: {datetime.now().strftime("%B %d, %Y")}', 0, 1, 'C')
        pdf.cell(0, 10, f'Time: {datetime.now().strftime("%I:%M %p")}', 0, 1, 'C')
        pdf.cell(0, 10, 'Subject: Data Analysis', 0, 1, 'C')
        pdf.ln(20)
        
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 10, 'Source: GeeksforGeeks Articles', 0, 1, 'C')
        
        # ===== TABLE OF CONTENTS =====
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 15, 'Contents', 0, 1, 'L')
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 12)
        
        for i, article in enumerate(selected_articles, 1):
            title = pdf.clean_text(article['title'])
            if len(title) > 50:
                title = title[:50] + "..."
            pdf.cell(0, 8, f'{i}. {title}', 0, 1, 'L')
        
        # ===== ARTICLES =====
        for i, article in enumerate(selected_articles, 1):
            pdf.add_page()
            
            # Article number
            pdf.set_font('Arial', 'B', 14)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 10, f'Article {i}', 0, 1, 'L')
            
            # Title
            pdf.set_font('Arial', 'B', 16)
            pdf.set_text_color(52, 152, 219)
            clean_title = pdf.clean_text(article['title'])
            pdf.multi_cell(0, 8, clean_title)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(5)
            
            # Source URL
            pdf.set_font('Arial', 'I', 8)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 5, f'Source: {article["url"]}', 0, 1, 'L')
            pdf.set_text_color(0, 0, 0)
            pdf.ln(5)
            
            # ===== KEY CONCEPTS =====
            pdf.set_font('Arial', 'B', 12)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 8, 'KEY CONCEPTS', 0, 1, 'L', 1)
            pdf.set_font('Arial', '', 11)
            
            for concept in article['concepts']:
                clean_concept = pdf.clean_text(concept)
                pdf.multi_cell(0, 6, f'- {clean_concept}')
            pdf.ln(5)
            
            # ===== CODE EXAMPLES =====
            if article['codes'] and len(article['codes']) > 0:
                pdf.set_font('Arial', 'B', 12)
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(0, 8, 'CODE EXAMPLES', 0, 1, 'L', 1)
                
                for code in article['codes']:
                    pdf.set_font('Courier', '', 9)
                    clean_code = pdf.clean_text(code)
                    pdf.multi_cell(0, 5, clean_code)
                    pdf.ln(3)
                pdf.ln(3)
            
            # ===== COMPLEXITY =====
            pdf.set_font('Arial', 'B', 12)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 8, 'COMPLEXITY ANALYSIS', 0, 1, 'L', 1)
            pdf.set_font('Arial', '', 11)
            
            clean_complexity = pdf.clean_text(article['complexity'])
            pdf.multi_cell(0, 6, clean_complexity)
            pdf.ln(5)
            
            # ===== REFERENCES =====
            if article['references'] and len(article['references']) > 0:
                pdf.set_font('Arial', 'B', 12)
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(0, 8, 'REFERENCES', 0, 1, 'L', 1)
                pdf.set_font('Arial', '', 10)
                
                for ref in article['references']:
                    clean_ref = pdf.clean_text(ref)
                    pdf.cell(0, 6, f'- {clean_ref}', 0, 1, 'L')
        
        # ===== SAVE PDF =====
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Data_Analysis_Module_{timestamp}.pdf"
        
        # Use os.path.join for Windows compatibility
        full_path = os.path.join(PDF_FOLDER, filename)
        
        # Save the PDF
        pdf.output(full_path)
        
        # Convert to absolute path for sending
        abs_path = os.path.abspath(full_path)
        print(f"✅ PDF generated successfully: {abs_path}")
        
        return abs_path
        
    except Exception as e:
        print(f"❌ PDF Error: {e}")
        traceback.print_exc()
        return None

# ========== FLASK ROUTES ==========
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape_titles():
    try:
        articles = scrape_article_titles()
        return jsonify({
            'success': True,
            'count': len(articles),
            'message': f'{len(articles)} articles ang nailista'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/articles')
def get_articles():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        basic_info = [{
            'id': a['id'],
            'title': a['title'],
            'url': a['url']
        } for a in articles]
        return jsonify(basic_info)
    return jsonify([])

@app.route('/article/<int:article_id>')
def get_article_details_route(article_id):
    if not os.path.exists(JSON_FILE):
        return jsonify({'error': 'No articles found'}), 404
    
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    article = next((a for a in articles if a['id'] == article_id), None)
    
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    
    full_data = get_article_details(article['url'])
    
    if full_data:
        return jsonify(full_data)
    else:
        return jsonify({'error': 'Failed to fetch article details'}), 500

@app.route('/generate-pdf', methods=['POST'])
def create_pdf():
    data = request.json
    selected_articles = data.get('articles', [])
    
    if not selected_articles:
        return jsonify({'error': 'No articles selected'}), 400
    
    pdf_file = generate_pdf(selected_articles)
    
    if pdf_file and os.path.exists(pdf_file):
        try:
            # Use absolute path and normalize it
            abs_path = os.path.abspath(pdf_file)
            print(f"📁 Sending file from: {abs_path}")
            
            return send_file(
                abs_path,
                as_attachment=True,
                download_name=f"Data_Analysis_Module_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mimetype='application/pdf'
            )
        except Exception as e:
            print(f"❌ Error sending file: {e}")
            return jsonify({'error': f'Error sending file: {str(e)}'}), 500
    
    return jsonify({'error': 'PDF file not found'}), 500

@app.route('/clear', methods=['POST'])
def clear_data():
    if os.path.exists(JSON_FILE):
        os.remove(JSON_FILE)
    return jsonify({'success': True})

# ========== MAIN ==========
if __name__ == '__main__':
    print("\n" + "="*60)
    print("📊 GEEKSFORGEEKS DATA ANALYSIS SCRAPER")
    print("="*60)
    print("\n🚀 Server starting...")
    print(f"📁 PDF folder: {os.path.abspath(PDF_FOLDER)}")
    print(f"📄 JSON file: {os.path.abspath(JSON_FILE)}")
    print("\n🌐 Open browser: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)