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
    get_page_links_by_category,
    crawl_sitemap_pages,
    parse_sitemap
)
from agent import seo_agent_app, link_categorization_agent_app

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
        report = result["final_report"]
        
        # Check if there was an error in the audit
        if isinstance(report, dict) and report.get("success") == False and "error" in report:
            return {
                "summary": "Audit Failed",
                "generated_insights": [],
                "raw_data": {},
                "error": report.get("error"),
                "message": report.get("message", report.get("error")),
                "access_blocked": report.get("access_blocked", False)
            }
        
        return report
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
        final_report = result["categorized_report"]
        
        # Extract the nested report structure
        if isinstance(final_report, dict) and "report" in final_report:
            actual_report = final_report.get("report", {})
            
            # Check if there was an error in the report
            if actual_report.get("success") == False and "error" in actual_report:
                return {
                    "total_links": 0,
                    "internal_links": 0,
                    "external_links": 0,
                    "quality_score": 0,
                    "categories": {},
                    "insights": [],
                    "warnings": [actual_report.get("message", actual_report.get("error", "Failed to fetch links"))],
                    "recommendations": [],
                    "all_links": [],
                    "error": actual_report.get("error"),
                    "access_blocked": actual_report.get("access_blocked", False)
                }
            
            # Flatten the category data and collect all links
            categories = {}
            all_links = []
            detailed_categories = actual_report.get("detailed_categories", {})
            
            for category_name, category_data in detailed_categories.items():
                links_in_category = category_data.get("links", [])
                categories[category_name] = {
                    "count": category_data.get("count", 0),
                    "examples": links_in_category[:3]  # Get first 3 examples
                }
                
                # Add all links from this category to the main list
                for link in links_in_category:
                    all_links.append({
                        "url": link.get("url", ""),
                        "anchor_text": link.get("anchor_text", "[No text]"),
                        "category": category_name,
                        "is_internal": link.get("is_internal", False),
                        "is_nofollow": link.get("is_nofollow", False),
                        "is_sponsored": link.get("is_sponsored", False),
                        "target": link.get("target", ""),
                    })
            
            # Return flattened response matching component expectations
            return {
                "total_links": actual_report.get("total_links", 0),
                "internal_links": actual_report.get("internal_links", 0),
                "external_links": actual_report.get("external_links", 0),
                "quality_score": actual_report.get("link_quality_score", 0),
                "categories": categories,
                "insights": actual_report.get("insights", []),
                "warnings": actual_report.get("warnings", []),
                "recommendations": actual_report.get("recommendations", []),
                "summary": actual_report.get("summary", ""),
                "all_links": all_links  # Send all links to frontend
            }
        
        return final_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Get port from environment variable (Required for Cloud Run / Render)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)