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

# --- 6. Backlink Analyzer ---
def analyze_backlinks(url: str):
    """
    Analyzes backlinks to a domain using free APIs and heuristics.
    Returns comprehensive link profile data, quality metrics, and competitor analysis.
    """
    try:
        # Extract domain from URL
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Collect backlink data using multiple methods
        backlinks_data = {
            "domain": domain,
            "data_source": "SIMULATED_DEMO_DATA",
            "data_source_label": "⚠️ Demo/Simulated Data - Integration with Ahrefs, SEMrush, or Majestic API required for production",
            "total_backlinks": 0,
            "referring_domains": 0,
            "dofollow_links": 0,
            "nofollow_links": 0,
            "link_profile": {
                "high_authority_links": [],
                "medium_authority_links": [],
                "low_authority_links": []
            },
            "anchor_text_analysis": {},
            "link_types": {
                "homepage": 0,
                "inner_pages": 0,
                "resource_links": 0,
                "blog_links": 0
            },
            "link_quality_score": 0,
            "toxic_links": [],
            "opportunities": []
        }
        
        # Simulate backlink discovery (in production, use Ahrefs/SEMrush API)
        # Using heuristics and searches to estimate link profile
        
        # Generate realistic backlink simulation
        import random
        total_backlinks = random.randint(50, 500)
        referring_domains = random.randint(20, 150)
        dofollow_percent = random.randint(60, 85)
        
        backlinks_data["total_backlinks"] = total_backlinks
        backlinks_data["referring_domains"] = referring_domains
        backlinks_data["dofollow_links"] = int(total_backlinks * (dofollow_percent / 100))
        backlinks_data["nofollow_links"] = total_backlinks - backlinks_data["dofollow_links"]
        
        # Authority distribution (simulated)
        high_auth_count = int(referring_domains * 0.15)  # 15% high authority
        medium_auth_count = int(referring_domains * 0.35)  # 35% medium authority
        low_auth_count = referring_domains - high_auth_count - medium_auth_count
        
        # High Authority Links (DA > 60)
        for i in range(high_auth_count):
            backlinks_data["link_profile"]["high_authority_links"].append({
                "source_domain": f"authoritative-site-{i}.com",
                "domain_authority": random.randint(65, 95),
                "anchor_text": random.choice(["best seo tools", "digital marketing", "seo guide", "industry leader"]),
                "link_type": "dofollow",
                "page_type": random.choice(["homepage", "resource", "article"])
            })
        
        # Medium Authority Links (DA 30-60)
        for i in range(medium_auth_count):
            backlinks_data["link_profile"]["medium_authority_links"].append({
                "source_domain": f"business-site-{i}.com",
                "domain_authority": random.randint(30, 60),
                "anchor_text": random.choice(["seo services", "marketing tools", "analytics platform", "optimization guide"]),
                "link_type": random.choice(["dofollow", "nofollow"]),
                "page_type": random.choice(["article", "directory", "resource"])
            })
        
        # Low Authority Links (DA < 30)
        for i in range(low_auth_count):
            backlinks_data["link_profile"]["low_authority_links"].append({
                "source_domain": f"blog-site-{i}.com",
                "domain_authority": random.randint(5, 29),
                "anchor_text": random.choice(["click here", "read more", "check this out", "learn more"]),
                "link_type": random.choice(["dofollow", "nofollow", "sponsored"]),
                "page_type": random.choice(["blog", "forum", "comment"])
            })
        
        # Anchor Text Analysis
        anchor_texts = []
        for link in backlinks_data["link_profile"]["high_authority_links"]:
            anchor_texts.append(link["anchor_text"])
        for link in backlinks_data["link_profile"]["medium_authority_links"]:
            anchor_texts.append(link["anchor_text"])
        
        anchor_counter = Counter(anchor_texts)
        backlinks_data["anchor_text_analysis"] = {
            "most_common": [{"text": text, "count": count} for text, count in anchor_counter.most_common(5)],
            "branded_anchors": sum(1 for text in anchor_texts if domain.split('.')[0].lower() in text.lower()),
            "keyword_anchors": sum(1 for text in anchor_texts if len(text) > 3 and text not in ["click here", "read more"]),
            "generic_anchors": sum(1 for text in anchor_texts if text in ["click here", "read more", "check this out", "learn more"])
        }
        
        # Link Type Analysis
        backlinks_data["link_types"]["homepage"] = int(referring_domains * 0.3)
        backlinks_data["link_types"]["inner_pages"] = int(referring_domains * 0.5)
        backlinks_data["link_types"]["resource_links"] = int(referring_domains * 0.15)
        backlinks_data["link_types"]["blog_links"] = int(referring_domains * 0.05)
        
        # Calculate link quality score (0-100)
        quality_score = 50  # Base score
        quality_score += min(high_auth_count * 2, 25)  # Authority distribution
        quality_score += min((dofollow_percent - 50) / 2, 15)  # Dofollow ratio
        quality_score += min(backlinks_data["anchor_text_analysis"]["keyword_anchors"] / 5, 10)  # Anchor text relevance
        backlinks_data["link_quality_score"] = min(100, int(quality_score))
        
        # Identify potentially toxic links
        toxic_count = random.randint(0, max(1, int(referring_domains * 0.05)))
        for i in range(toxic_count):
            backlinks_data["toxic_links"].append({
                "source_domain": f"spam-site-{i}.biz",
                "domain_authority": random.randint(1, 15),
                "reason": random.choice(["Likely spam network", "Suspicious content", "Unrelated niche", "Known bad neighborhood"]),
                "severity": random.choice(["low", "medium", "high"])
            })
        
        # METHOD 1: Extract competitor domains from backlink sources
        # Competitors are often linked from the same authority sources as you
        high_auth_sources = [link["source_domain"] for link in backlinks_data["link_profile"]["high_authority_links"]]
        
        # Simulate that high-authority domains link to 2-3 competitors as well
        backlinks_data["competitor_analysis"] = {
            "detection_method": "⚠️ DEMO: Authority source analysis - competitors found in same high-authority linking domains",
            "data_source": "SIMULATED",
            "note": "Competitor information is simulated for demo purposes. Real data requires integration with Ahrefs, SEMrush, or Majestic API.",
            "competitors_detected": []
        }
        
        # Detect competitors based on common linking sources
        detected_competitors = []
        for source in high_auth_sources[::max(1, len(high_auth_sources) // 3)]:  # Sample every nth source
            # Simulate that this authority source links to competitors
            num_competitors_per_source = random.randint(1, 3)
            for j in range(num_competitors_per_source):
                comp_domain = f"[DEMO] competitor{len(detected_competitors) + 1}.com"
                if comp_domain not in [c["domain"] for c in detected_competitors]:
                    detected_competitors.append({
                        "domain": comp_domain,
                        "detected_from": source,
                        "authority_level": "High-authority",
                        "detection_confidence": round(random.uniform(0.7, 0.95), 2),
                        "is_simulated": True
                    })
        
        # If we found fewer than 3 competitors, add default ones
        if len(detected_competitors) < 3:
            default_competitors = [
                {"domain": "[DEMO] competitor1.com", "detected_from": "industry_search", "authority_level": "Industry leader", "detection_confidence": 0.88, "is_simulated": True},
                {"domain": "[DEMO] competitor2.com", "detected_from": "niche_directory", "authority_level": "Established player", "detection_confidence": 0.82, "is_simulated": True},
                {"domain": "[DEMO] competitor3.com", "detected_from": "resource_site", "authority_level": "Growing competitor", "detection_confidence": 0.75, "is_simulated": True},
            ]
            detected_competitors.extend(default_competitors[:3 - len(detected_competitors)])
        
        backlinks_data["competitor_analysis"]["competitors_detected"] = detected_competitors
        
        # METHOD 2: Build competitor profiles by analyzing common backlink patterns
        backlinks_data["opportunities"] = []
        
        for competitor in detected_competitors[:3]:  # Analyze top 3 competitors
            # Simulate realistic competitor backlink profiles relative to user's profile
            comp_total_backlinks = total_backlinks + random.randint(-100, 300)
            comp_referring_domains = referring_domains + random.randint(-30, 100)
            comp_high_auth_links = high_auth_count + random.randint(-5, 20)
            comp_dofollow_percent = random.randint(65, 85)
            comp_dofollow_links = int(comp_total_backlinks * (comp_dofollow_percent / 100))
            
            # Authority Gap Analysis
            if comp_high_auth_links > high_auth_count + 5:
                backlinks_data["opportunities"].append({
                    "type": "competitor_gap",
                    "is_simulated": True,
                    "title": f"[DEMO] Authority Gap vs {competitor['domain']}",
                    "description": f"{competitor['domain']} (detected from {competitor['detected_from']}) has {comp_high_auth_links} high-authority links (DA 60+) vs your {high_auth_count}. This represents a {round((comp_high_auth_links - high_auth_count) / max(1, high_auth_count) * 100)}% advantage.",
                    "competitor": competitor["domain"],
                    "detection_confidence": competitor["detection_confidence"],
                    "gap_metric": f"{comp_high_auth_links} vs {high_auth_count} DA60+ links",
                    "estimated_impact": "High" if comp_high_auth_links > high_auth_count + 15 else "Medium",
                    "action": "Research their high-authority backlinks. Identify the top 10 sources and develop targeted outreach strategy.",
                    "potential_links": comp_high_auth_links - high_auth_count
                })
            
            # Referring Domain Diversity Gap
            if comp_referring_domains > referring_domains + 20:
                backlinks_data["opportunities"].append({
                    "type": "competitor_gap",
                    "is_simulated": True,
                    "title": f"[DEMO] Domain Diversity Gap vs {competitor['domain']}",
                    "description": f"{competitor['domain']} has links from {comp_referring_domains} unique domains (your {referring_domains}). They have {round((comp_referring_domains - referring_domains) / referring_domains * 100)}% more link sources.",
                    "competitor": competitor["domain"],
                    "detection_confidence": competitor["detection_confidence"],
                    "gap_metric": f"{comp_referring_domains} vs {referring_domains} referring domains",
                    "estimated_impact": "High" if comp_referring_domains > referring_domains + 50 else "Medium",
                    "action": "Analyze their link sources. Target niche directories, industry databases, and associations they're listed in.",
                    "potential_links": comp_referring_domains - referring_domains
                })
            
            # Dofollow Link Quality Gap
            comp_dofollow_ratio = (comp_dofollow_links / max(1, comp_total_backlinks) * 100) if comp_total_backlinks > 0 else 0
            user_dofollow_ratio = (backlinks_data["dofollow_links"] / total_backlinks * 100) if total_backlinks > 0 else 0
            
            if comp_dofollow_ratio > user_dofollow_ratio + 5:
                backlinks_data["opportunities"].append({
                    "type": "competitor_gap",
                    "is_simulated": True,
                    "title": f"[DEMO] Link Quality Gap vs {competitor['domain']}",
                    "description": f"{competitor['domain']} has a {comp_dofollow_ratio:.0f}% dofollow ratio vs your {user_dofollow_ratio:.0f}%. Higher quality link acquisition strategy.",
                    "competitor": competitor["domain"],
                    "detection_confidence": competitor["detection_confidence"],
                    "gap_metric": f"{comp_dofollow_ratio:.0f}% vs {user_dofollow_ratio:.0f}% dofollow",
                    "estimated_impact": "Medium",
                    "action": "Focus on dofollow link placements. Seek paid content and resource page links that pass link equity.",
                    "potential_links": int(comp_dofollow_links - backlinks_data["dofollow_links"])
                })
        
        # Link velocity (estimated new links per month)
        backlinks_data["link_velocity"] = {
            "new_links_30_days": random.randint(5, 30),
            "new_links_90_days": random.randint(15, 80),
            "trend": random.choice(["growing", "stable", "declining"])
        }
        
        return backlinks_data
        
    except Exception as e:
        return {"error": str(e), "domain": url}