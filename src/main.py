import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Import our tools and agent
import tools
from agent import seo_agent_app

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

if __name__ == "__main__":
    # Get port from environment variable (Required for Cloud Run / Render)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)