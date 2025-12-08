import os
import sys
import time
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import our tools and agent
from tools import (
    extract_meta_tags, 
    check_broken_links, 
    analyze_backlinks,
    extract_page_backlinks,
    get_page_links_by_category,
    crawl_sitemap_pages,
    parse_sitemap
)
from agent import seo_agent_app, backlinks_agent_app, link_categorization_agent_app

app = FastAPI(title="SEO Agent API", version="1.0")

# --- CORS Configuration ---
# In production, set FRONTEND_URL to your React app's domain (e.g., https://my-seo-app.vercel.app)
frontend_url = os.getenv("FRONTEND_URL", "*")
origins = [frontend_url] if frontend_url != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class UrlRequest(BaseModel):
    url: str

class KeywordRequest(BaseModel):
    keyword: str

class AuditRequest(BaseModel):
    url: str
    focus_areas: Optional[List[str]] = ["all"]

class SitemapRequest(BaseModel):
    sitemap_url: str
    max_pages: Optional[int] = 50

class UrlListRequest(BaseModel):
    urls: List[str]  # Comma-separated or list of URLs

# --- 1. Tool Belt API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "SEO Agent Online", "docs_url": "/docs"}

@app.post("/tools/meta")
def tool_meta_tags(request: UrlRequest):
    return tools.extract_meta_tags(request.url)

@app.post("/tools/speed")
def tool_page_speed(request: UrlRequest):
    return tools.get_page_speed(request.url)

@app.post("/tools/broken-links")
def tool_broken_links(request: UrlRequest):
    return tools.check_broken_links(request.url, limit=5)

@app.post("/tools/serp")
def tool_serp_check(request: KeywordRequest):
    return tools.get_competitor_rankings(request.keyword)

@app.post("/tools/keywords")
def tool_keyword_density(request: UrlRequest):
    return tools.analyze_keyword_density(url=request.url)

@app.post("/tools/page-backlinks")
def tool_extract_backlinks(request: UrlRequest):
    """Extract all outbound links (backlinks) from a given page"""
    return extract_page_backlinks(url=request.url)

@app.post("/tools/links-by-category")
def tool_categorized_links(request: UrlRequest):
    """Extract all links from a page and categorize them"""
    return get_page_links_by_category(url=request.url)

@app.post("/tools/sitemap-parse")
def tool_parse_sitemap(request: SitemapRequest):
    """Parse a sitemap XML and extract all URLs"""
    return parse_sitemap(sitemap_url=request.sitemap_url)

@app.post("/tools/sitemap-crawl")
def tool_crawl_sitemap(request: SitemapRequest):
    """Crawl all pages from a sitemap and extract categorized links from each"""
    return crawl_sitemap_pages(
        sitemap_url=request.sitemap_url,
        max_pages=request.max_pages
    )

@app.post("/tools/urls-batch-analyze")
def tool_batch_analyze_urls(request: UrlListRequest):
    """Analyze multiple URLs and extract categorized links from each"""
    results = []
    for url in request.urls:
        try:
            link_data = get_page_links_by_category(url=url)
            results.append(link_data)
            time.sleep(0.3)  # Rate limiting
        except Exception as e:
            results.append({"error": str(e), "url": url})
    
    return {
        "total_urls_analyzed": len(request.urls),
        "successful": len([r for r in results if 'error' not in r]),
        "failed": len([r for r in results if 'error' in r]),
        "results": results
    }

# --- 2. Orchestrated Agent Endpoint ---

@app.post("/agent/audit")
def run_audit_agent(request: AuditRequest):
    initial_state = {
        "url": request.url,
        "objectives": request.focus_areas,
        "audit_data": {},
        "final_report": "",
        "errors": []
    }
    
    try:
        # Invoke LangGraph workflow
        result = seo_agent_app.invoke(initial_state)
        return result["final_report"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/backlinks")
def run_backlinks_agent(request: UrlRequest):
    initial_state = {
        "url": request.url,
        "backlinks_data": {},
        "analysis_report": {},
        "errors": []
    }
    
    try:
        # Invoke LangGraph backlinks workflow
        result = backlinks_agent_app.invoke(initial_state)
        return result["analysis_report"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/link-categorization")
def run_link_categorization_agent(request: UrlRequest):
    """
    Run the Link Categorization Agent to collect all links on a page,
    categorize them, and provide insights and recommendations.
    """
    initial_state = {
        "url": request.url,
        "links_data": {},
        "categorized_report": {},
        "errors": []
    }
    
    try:
        # Invoke LangGraph link categorization workflow
        result = link_categorization_agent_app.invoke(initial_state)
        return result["categorized_report"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Get port from environment variable (Required for Cloud Run / Render)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)