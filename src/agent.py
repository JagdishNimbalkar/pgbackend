from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from tools import extract_meta_tags, get_page_speed, analyze_keyword_density, check_broken_links, analyze_backlinks, extract_page_backlinks

# 1. Define Agent State
class AgentState(TypedDict):
    url: str
    objectives: List[str]  # e.g. ["technical", "content", "speed"]
    audit_data: Dict[str, Any]
    final_report: str
    errors: List[str]

# 2. Define Nodes (Steps in the workflow)

def node_config(state: AgentState):
    """Initializes the audit data structure."""
    print(f"--- STARTING AUDIT FOR: {state['url']} ---")
    return {"audit_data": {}, "errors": []}

def node_technical_audit(state: AgentState):
    """Runs technical scraping tools."""
    print("--- RUNNING TECHNICAL AUDIT ---")
    url = state["url"]
    existing_data = state["audit_data"]
    
    # Run tools
    meta = extract_meta_tags(url)
    broken_links = check_broken_links(url, limit=5)
    
    existing_data["technical"] = {
        "meta_tags": meta,
        "broken_links": broken_links
    }
    return {"audit_data": existing_data}

def node_performance_audit(state: AgentState):
    """Runs performance checks."""
    print("--- RUNNING PERFORMANCE AUDIT ---")
    url = state["url"]
    existing_data = state["audit_data"]
    
    speed = get_page_speed(url)
    existing_data["performance"] = speed
    
    return {"audit_data": existing_data}

def node_content_analysis(state: AgentState):
    """Runs content and keyword analysis."""
    print("--- RUNNING CONTENT ANALYSIS ---")
    url = state["url"]
    existing_data = state["audit_data"]
    
    # We pass the URL directly to the tool to fetch text fresh
    keywords = analyze_keyword_density(url=url)
    existing_data["content"] = keywords
    
    return {"audit_data": existing_data}

def node_report_generator(state: AgentState):
    """
    synthesizes the data into a final report.
    In a real scenario, this is where the LLM (GPT-4) would generate text.
    For this tool belt, we will structure a JSON summary.
    """
    print("--- GENERATING REPORT ---")
    data = state["audit_data"]
    
    # Simple rule-based insight generation (Simulating LLM logic)
    insights = []
    
    # Technical Insights
    title = data.get("technical", {}).get("meta_tags", {}).get("title", "")
    if len(title) < 10 or len(title) > 60:
        insights.append(f"Critical: Title tag length ({len(title)} chars) is non-optimal. Aim for 30-60 chars.")
    
    # Performance Insights
    load_time = data.get("performance", {}).get("load_time_ms", 0)
    if load_time > 1000:
        insights.append(f"Warning: Page load time is high ({load_time}ms). Consider optimizing images.")

    report = {
        "summary": "Audit Complete",
        "generated_insights": insights,
        "raw_data": data
    }
    
    return {"final_report": report}

# 3. Build the Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("setup", node_config)
workflow.add_node("technical", node_technical_audit)
workflow.add_node("performance", node_performance_audit)
workflow.add_node("content", node_content_analysis)
workflow.add_node("reporter", node_report_generator)

# Define Edges (Linear workflow for this version)
workflow.set_entry_point("setup")
workflow.add_edge("setup", "technical")
workflow.add_edge("technical", "performance")
workflow.add_edge("performance", "content")
workflow.add_edge("content", "reporter")
workflow.add_edge("reporter", END)

# Compile
seo_agent_app = workflow.compile()

# ============================================
# BACKLINK ANALYZER AGENT
# ============================================

class BacklinksState(TypedDict):
    url: str
    backlinks_data: Dict[str, Any]
    analysis_report: Dict[str, Any]
    errors: List[str]

def node_backlinks_setup(state: BacklinksState):
    """Initializes the backlinks analysis."""
    print(f"--- STARTING BACKLINKS ANALYSIS FOR: {state['url']} ---")
    return {"backlinks_data": {}, "analysis_report": {}, "errors": []}

def node_collect_backlinks(state: BacklinksState):
    """Collects backlink data."""
    print("--- COLLECTING BACKLINK DATA ---")
    url = state["url"]
    
    backlinks = analyze_backlinks(url)
    return {"backlinks_data": backlinks}

def node_analyze_link_profile(state: BacklinksState):
    """Analyzes link profile and generates insights."""
    print("--- ANALYZING LINK PROFILE ---")
    data = state["backlinks_data"]
    
    if "error" in data:
        return {"errors": [data["error"]]}
    
    insights = []
    recommendations = []
    
    # Analyze link distribution
    total_backlinks = data.get("total_backlinks", 0)
    referring_domains = data.get("referring_domains", 0)
    
    if total_backlinks == 0:
        insights.append("No backlinks detected. This is critical for SEO performance.")
        recommendations.append("Start outreach and link building campaigns immediately.")
    elif referring_domains > 0:
        avg_links_per_domain = total_backlinks / referring_domains
        if avg_links_per_domain > 5:
            insights.append(f"Strong link diversity: Average {avg_links_per_domain:.1f} links per domain.")
        else:
            insights.append(f"Limited link diversity: Only {avg_links_per_domain:.1f} links per domain on average.")
            recommendations.append("Diversify your link sources across more domains.")
    
    # Analyze dofollow vs nofollow
    dofollow_ratio = (data.get("dofollow_links", 0) / total_backlinks * 100) if total_backlinks > 0 else 0
    if dofollow_ratio < 50:
        insights.append(f"Low dofollow ratio ({dofollow_ratio:.0f}%). Many links may not pass link equity.")
        recommendations.append("Focus on acquiring high-quality dofollow links from authoritative sites.")
    else:
        insights.append(f"Healthy dofollow ratio ({dofollow_ratio:.0f}%) - good link equity transfer.")
    
    # Analyze authority distribution
    high_auth = len(data.get("link_profile", {}).get("high_authority_links", []))
    total_links_counted = high_auth + len(data.get("link_profile", {}).get("medium_authority_links", [])) + len(data.get("link_profile", {}).get("low_authority_links", []))
    
    if high_auth > 0 and total_links_counted > 0:
        high_auth_percent = (high_auth / total_links_counted * 100)
        if high_auth_percent >= 15:
            insights.append(f"Excellent link profile: {high_auth_percent:.0f}% of links from high-authority domains (DA > 60).")
        else:
            insights.append(f"Need more authority links: Only {high_auth_percent:.0f}% from high-authority domains.")
            recommendations.append("Target high-authority publications and resources for guest posting.")
    
    # Analyze anchor text
    anchor_analysis = data.get("anchor_text_analysis", {})
    branded = anchor_analysis.get("branded_anchors", 0)
    keyword = anchor_analysis.get("keyword_anchors", 0)
    generic = anchor_analysis.get("generic_anchors", 0)
    
    if keyword > 0:
        insights.append(f"Strong keyword anchors: {keyword} links use keyword-rich anchor text.")
    
    if generic > branded and generic > keyword:
        insights.append(f"Many generic anchors ({generic}). Consider improving anchor text diversity.")
        recommendations.append("Work with content partners to use descriptive anchor text in future links.")
    
    # Analyze toxic links
    toxic_links = data.get("toxic_links", [])
    if toxic_links:
        high_severity = len([l for l in toxic_links if l.get("severity") == "high"])
        insights.append(f"Found {len(toxic_links)} potentially toxic links ({high_severity} high-severity).")
        recommendations.append("Review and disavow toxic links using Google Search Console.")
    else:
        insights.append("Clean backlink profile - no obvious toxic links detected.")
    
    # Quality score interpretation
    quality_score = data.get("link_quality_score", 0)
    if quality_score >= 80:
        insights.append(f"Excellent link quality score: {quality_score}/100. Your backlink profile is strong.")
    elif quality_score >= 60:
        insights.append(f"Good link quality score: {quality_score}/100. There's room for improvement.")
    else:
        insights.append(f"Low link quality score: {quality_score}/100. Significant improvements needed.")
    
    # Link velocity
    velocity = data.get("link_velocity", {})
    trend = velocity.get("trend", "stable")
    new_30 = velocity.get("new_links_30_days", 0)
    
    if trend == "growing" and new_30 > 10:
        insights.append(f"Positive trend: Growing backlinks ({new_30} new in last 30 days).")
    elif trend == "declining":
        insights.append(f"Warning: Declining backlinks - lost some links recently.")
        recommendations.append("Analyze lost links and recreate valuable content to recover lost links.")
    
    report = {
        "summary": f"Analyzed {total_backlinks} backlinks from {referring_domains} unique domains",
        "quality_score": quality_score,
        "insights": insights,
        "recommendations": recommendations,
        "data_summary": {
            "total_backlinks": total_backlinks,
            "referring_domains": referring_domains,
            "dofollow_links": data.get("dofollow_links", 0),
            "nofollow_links": data.get("nofollow_links", 0),
            "high_authority_count": high_auth,
            "toxic_links_count": len(toxic_links)
        }
    }
    
    return {"analysis_report": report}

def node_backlinks_report_generator(state: BacklinksState):
    """Generates final backlinks report combining data and analysis."""
    print("--- GENERATING BACKLINKS REPORT ---")
    
    final_report = {
        "type": "backlinks_analysis",
        "backlinks_data": state.get("backlinks_data", {}),
        "analysis": state.get("analysis_report", {}),
        "errors": state.get("errors", [])
    }
    
    return {"analysis_report": final_report}

# Build the Backlinks Workflow
backlinks_workflow = StateGraph(BacklinksState)

backlinks_workflow.add_node("setup", node_backlinks_setup)
backlinks_workflow.add_node("collect", node_collect_backlinks)
backlinks_workflow.add_node("analyze", node_analyze_link_profile)
backlinks_workflow.add_node("reporter", node_backlinks_report_generator)

backlinks_workflow.set_entry_point("setup")
backlinks_workflow.add_edge("setup", "collect")
backlinks_workflow.add_edge("collect", "analyze")
backlinks_workflow.add_edge("analyze", "reporter")
backlinks_workflow.add_edge("reporter", END)

backlinks_agent_app = backlinks_workflow.compile()