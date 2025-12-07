import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import time
from duckduckgo_search import DDGS

# --- 1. Technical Scraper ---
def extract_meta_tags(url: str):
    """
    Scrapes a URL to extract SEO-relevant meta tags (Title, Description, H1-H3).
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        data = {
            "url": url,
            "title": soup.title.string if soup.title else "No Title Found",
            "meta_description": "No Description Found",
            "h1": [h.get_text(strip=True) for h in soup.find_all('h1')],
            "h2": [h.get_text(strip=True) for h in soup.find_all('h2')],
            "images_missing_alt": len([img for img in soup.find_all('img') if not img.get('alt')])
        }

        # Safe extraction of meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            data["meta_description"] = meta_desc.get('content', "No Description Found")
            
        return data
    except Exception as e:
        return {"error": str(e)}

# --- 2. Broken Link Checker (Lightweight) ---
def check_broken_links(url: str, limit: int = 10):
    """
    Finds links on the page and checks their status code. 
    Limited to 'limit' links to prevent long wait times during demos.
    """
    try:
        headers = {'User-Agent': 'SEO-Agent/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        links = [a.get('href') for a in soup.find_all('a', href=True) if a.get('href').startswith('http')]
        unique_links = list(set(links))[:limit]
        
        results = []
        for link in unique_links:
            try:
                r = requests.head(link, headers=headers, timeout=5)
                status = "Broken" if r.status_code >= 400 else "OK"
                results.append({"link": link, "status": status, "code": r.status_code})
            except:
                results.append({"link": link, "status": "Error", "code": 0})
                
        return {"checked_count": len(results), "details": results}
    except Exception as e:
        return {"error": str(e)}

# --- 3. Performance Estimator ---
def get_page_speed(url: str):
    """
    Estimates page load performance based on server response time and content size.
    Note: For production, integrate Google PageSpeed Insights API.
    """
    try:
        start_time = time.time()
        headers = {'User-Agent': 'SEO-Agent/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        end_time = time.time()
        
        duration = round((end_time - start_time) * 1000, 2) # ms
        size_kb = round(len(response.content) / 1024, 2)
        
        score = 100
        if duration > 1000: score -= 10
        if duration > 2000: score -= 20
        if size_kb > 2000: score -= 10
        
        return {
            "load_time_ms": duration,
            "page_size_kb": size_kb,
            "estimated_score": max(0, score),
            "status": "Good" if duration < 800 else "Needs Improvement"
        }
    except Exception as e:
        return {"error": str(e)}

# --- 4. Keyword Analyzer ---
def analyze_keyword_density(text: str = "", url: str = None):
    """
    Analyzes keyword frequency on a page.
    """
    content = text
    if url:
        try:
            headers = {'User-Agent': 'SEO-Agent/1.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.extract()
            content = soup.get_text()
        except Exception as e:
            return {"error": str(e)}

    # Simple Tokenization
    words = re.findall(r'\w+', content.lower())
    # Filter common stop words (simplified list)
    stop_words = set(['the', 'and', 'is', 'in', 'it', 'to', 'of', 'for', 'on', 'a', 'an', 'that', 'this', 'with'])
    filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
    
    counter = Counter(filtered_words)
    top_keywords = counter.most_common(10)
    
    return {"top_keywords": [{"word": w, "count": c} for w, c in top_keywords], "total_words": len(filtered_words)}

# --- 5. SERP Spy (Competitor Analysis) ---
def get_competitor_rankings(keyword: str):
    """
    Uses DuckDuckGo to find who is ranking for a specific keyword.
    """
    try:
        results = DDGS().text(keyword, max_results=5)
        return {"keyword": keyword, "competitors": results}
    except Exception as e:
        return {"error": str(e)}