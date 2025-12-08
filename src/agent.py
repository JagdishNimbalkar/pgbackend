from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from tools import (
    extract_meta_tags, 
    get_page_speed, 
    analyze_keyword_density, 
    check_broken_links, 
    analyze_backlinks, 
    extract_page_backlinks,
    get_page_links_by_category,
    crawl_sitemap_pages
)

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

# ============================================
# LINK CATEGORIZATION AGENT
# ============================================

class LinkCategorizationState(TypedDict):
    url: str
    links_data: Dict[str, Any]
    categorized_report: Dict[str, Any]
    errors: List[str]

def node_links_setup(state: LinkCategorizationState):
    """Initializes the link categorization analysis."""
    print(f"--- STARTING LINK CATEGORIZATION FOR: {state['url']} ---")
    return {"links_data": {}, "categorized_report": {}, "errors": []}

def node_collect_and_categorize_links(state: LinkCategorizationState):
    """Collects all links from the page and categorizes them."""
    print("--- COLLECTING AND CATEGORIZING LINKS ---")
    url = state["url"]
    
    try:
        links_data = get_page_links_by_category(url)
        return {"links_data": links_data}
    except Exception as e:
        return {"errors": [f"Error collecting links: {str(e)}"]}

def node_analyze_link_categories(state: LinkCategorizationState):
    """Analyzes the categorized links and generates insights."""
    print("--- ANALYZING LINK CATEGORIES ---")
    data = state["links_data"]
    
    if state.get("errors"):
        return {"categorized_report": {"error": state["errors"][0]}}
    
    if "error" in data:
        return {"errors": [data["error"]], "categorized_report": {"error": data["error"]}}
    
    insights = []
    recommendations = []
    warnings = []
    
    total_links = data.get("total_links", 0)
    categories = data.get("categories", {})
    page_domain = data.get("page_domain", "")
    
    if total_links == 0:
        insights.append("No links found on this page.")
        warnings.append("Pages with no links may have poor user experience and limited SEO value.")
        return {"categorized_report": {
            "summary": "No links detected",
            "insights": insights,
            "warnings": warnings
        }}
    
    # Analyze each category
    category_stats = {}
    for category_name, category_data in categories.items():
        count = category_data.get("count", 0)
        if count > 0:
            category_stats[category_name] = {
                "count": count,
                "percentage": round((count / total_links * 100), 1),
                "description": category_data.get("description", "")
            }
    
    # Navigation links analysis
    nav_count = categories.get("navigation", {}).get("count", 0)
    if nav_count == 0:
        warnings.append("No navigation links detected. Users may have difficulty navigating your site.")
        recommendations.append("Add clear navigation links (home, about, contact, services) to improve user experience.")
    elif nav_count < 5:
        insights.append(f"Limited navigation: Only {nav_count} navigation links found.")
        recommendations.append("Consider adding more navigation options for better site structure.")
    else:
        insights.append(f"Good navigation structure: {nav_count} navigation links found.")
    
    # Social media links analysis
    social_count = categories.get("social", {}).get("count", 0)
    if social_count == 0:
        recommendations.append("Add social media links to increase brand visibility and engagement.")
    else:
        insights.append(f"Social presence: {social_count} social media links found.")
    
    # Legal pages analysis
    legal_count = categories.get("legal", {}).get("count", 0)
    if legal_count == 0:
        warnings.append("No legal/policy links found. This may affect user trust and compliance.")
        recommendations.append("Add privacy policy, terms of service, and other compliance pages.")
    else:
        insights.append(f"Legal compliance: {legal_count} legal/policy links present.")
    
    # Business/Content links analysis
    business_count = categories.get("business", {}).get("count", 0)
    if business_count == 0:
        warnings.append("No business/content links found. Add blog posts, resources, or product pages.")
    else:
        insights.append(f"Content depth: {business_count} business/content links found.")
    
    # External links analysis
    external_count = categories.get("external", {}).get("count", 0)
    external_percentage = (external_count / total_links * 100) if total_links > 0 else 0
    
    if external_count == 0:
        warnings.append("No external links found. Consider linking to authoritative sources to build trust.")
        recommendations.append("Add relevant external links to trusted sources in your industry.")
    elif external_percentage > 70:
        warnings.append(f"High external link ratio ({external_percentage:.0f}%). This may dilute your link equity.")
        recommendations.append("Balance external links with more internal linking to keep users on your site.")
    else:
        insights.append(f"Balanced external linking: {external_count} external links ({external_percentage:.0f}%).")
    
    # Check for nofollow attributes on external links
    external_links = categories.get("external", {}).get("links", [])
    nofollow_external = sum(1 for link in external_links if link.get("is_nofollow", False))
    if nofollow_external > 0 and external_count > 0:
        nofollow_pct = (nofollow_external / external_count * 100)
        insights.append(f"{nofollow_pct:.0f}% of external links use nofollow attribute (good for link juice preservation).")
    
    # Media links analysis
    media_count = categories.get("media", {}).get("count", 0)
    if media_count > 0:
        insights.append(f"Rich content: {media_count} media/download links found.")
    
    # Utility links analysis
    utility_count = categories.get("utility", {}).get("count", 0)
    if utility_count > 10:
        insights.append(f"Many utility links ({utility_count}). Ensure they don't clutter the user experience.")
    
    # Internal vs External ratio
    internal_count = total_links - external_count
    if internal_count > 0 and external_count > 0:
        ratio = internal_count / external_count
        if ratio >= 3:
            insights.append(f"Excellent internal linking: {ratio:.1f}:1 ratio of internal to external links.")
        elif ratio >= 1.5:
            insights.append(f"Good internal linking: {ratio:.1f}:1 ratio of internal to external links.")
        else:
            warnings.append(f"Low internal linking ratio: {ratio:.1f}:1. Consider adding more internal links.")
            recommendations.append("Strengthen internal linking to improve site structure and SEO.")
    
    # Link quality checks
    all_links = []
    for category_data in categories.values():
        all_links.extend(category_data.get("links", []))
    
    # Count links without anchor text
    no_anchor_text = sum(1 for link in all_links if link.get("anchor_text", "") in ["", "[No text]"])
    if no_anchor_text > 0:
        warnings.append(f"{no_anchor_text} links have no anchor text. This is bad for accessibility and SEO.")
        recommendations.append("Add descriptive anchor text to all links for better user experience and SEO.")
    
    # Count sponsored links
    sponsored_count = sum(1 for link in all_links if link.get("is_sponsored", False))
    if sponsored_count > 0:
        insights.append(f"{sponsored_count} links properly marked as sponsored.")
    
    # Generate overall score
    score = 70  # Base score
    
    # Add points for good practices
    if nav_count >= 5: score += 5
    if social_count > 0: score += 3
    if legal_count > 0: score += 5
    if business_count >= 10: score += 5
    if 0.2 <= external_percentage <= 30: score += 7
    if no_anchor_text == 0: score += 5
    
    # Subtract points for issues
    if nav_count == 0: score -= 10
    if legal_count == 0: score -= 5
    if external_percentage > 70: score -= 10
    if no_anchor_text > total_links * 0.2: score -= 10
    
    score = max(0, min(100, score))  # Clamp between 0-100
    
    report = {
        "summary": f"Analyzed {total_links} links across 7 categories from {page_domain}",
        "link_quality_score": score,
        "total_links": total_links,
        "internal_links": internal_count,
        "external_links": external_count,
        "category_breakdown": category_stats,
        "insights": insights,
        "warnings": warnings,
        "recommendations": recommendations,
        "detailed_categories": categories
    }
    
    return {"categorized_report": report}

def node_links_report_generator(state: LinkCategorizationState):
    """Generates final link categorization report."""
    print("--- GENERATING LINK CATEGORIZATION REPORT ---")
    
    final_report = {
        "type": "link_categorization_analysis",
        "url": state.get("url", ""),
        "report": state.get("categorized_report", {}),
        "raw_data": state.get("links_data", {}),
        "errors": state.get("errors", [])
    }
    
    return {"categorized_report": final_report}

# Build the Link Categorization Workflow
links_workflow = StateGraph(LinkCategorizationState)

links_workflow.add_node("setup", node_links_setup)
links_workflow.add_node("collect", node_collect_and_categorize_links)
links_workflow.add_node("analyze", node_analyze_link_categories)
links_workflow.add_node("reporter", node_links_report_generator)

links_workflow.set_entry_point("setup")
links_workflow.add_edge("setup", "collect")
links_workflow.add_edge("collect", "analyze")
links_workflow.add_edge("analyze", "reporter")
links_workflow.add_edge("reporter", END)

link_categorization_agent_app = links_workflow.compile()