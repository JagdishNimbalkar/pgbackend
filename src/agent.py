from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from operator import add
from tools import (
    extract_meta_tags, 
    get_page_speed, 
    analyze_keyword_density, 
    check_broken_links, 
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
    
    try:
        # Run tools
        meta = extract_meta_tags(url)
        
        # Check if tools returned errors
        if isinstance(meta, dict) and "error" in meta:
            existing_data["technical"] = {
                "error": meta.get("error"),
                "message": meta.get("message"),
                "access_blocked": meta.get("access_blocked", False)
            }
            error_msg = f"Technical audit failed: {meta.get('error')}"
            return {"audit_data": existing_data, "errors": [error_msg]}
        
        broken_links = check_broken_links(url, limit=5)
        
        existing_data["technical"] = {
            "meta_tags": meta,
            "broken_links": broken_links
        }
        return {"audit_data": existing_data}
    except Exception as e:
        return {"errors": [f"Technical audit error: {str(e)}"]}


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
    errors = state.get("errors", [])
    
    # Check if there were errors during audit
    if errors:
        error_msg = errors[0]
        # Check if technical audit had access blocked info
        access_blocked = data.get("technical", {}).get("access_blocked", False) if isinstance(data.get("technical"), dict) else False
        
        report = {
            "summary": "Audit Failed",
            "error": error_msg.replace("Technical audit failed: ", ""),
            "message": error_msg,
            "success": False,
            "access_blocked": access_blocked,
            "generated_insights": [],
            "raw_data": data
        }
        return {"final_report": report}
    
    # Check if technical audit had errors
    if isinstance(data.get("technical"), dict) and "error" in data.get("technical", {}):
        tech_error = data["technical"]
        report = {
            "summary": "Audit Failed",
            "error": tech_error["error"],
            "message": tech_error.get("message"),
            "success": False,
            "access_blocked": tech_error.get("access_blocked", False),
            "generated_insights": [],
            "raw_data": data
        }
        return {"final_report": report}
    
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
        "raw_data": data,
        "success": True
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
        return {
            "categorized_report": {
                "error": state["errors"][0],
                "success": False
            }
        }
    
    if "error" in data:
        # Check if this is an access blocked error
        if data.get("access_blocked"):
            error_message = data.get("message", "Website is blocking automated access")
            return {
                "categorized_report": {
                    "error": data["error"],
                    "message": error_message,
                    "success": False,
                    "access_blocked": True
                }
            }
        else:
            error_message = data.get("message", f"Failed to fetch links: {data['error']}")
            return {
                "categorized_report": {
                    "error": data["error"],
                    "message": error_message,
                    "success": False
                }
            }
    
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
            "warnings": warnings,
            "success": False
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
    
    # E-commerce links analysis
    ecommerce_count = categories.get("ecommerce", {}).get("count", 0)
    product_count = categories.get("product", {}).get("count", 0)
    if ecommerce_count > 0 or product_count > 0:
        total_shopping = ecommerce_count + product_count
        insights.append(f"E-commerce presence: {total_shopping} shopping/product links found ({ecommerce_count} commerce, {product_count} products).")
        if ecommerce_count > 0 and product_count == 0:
            recommendations.append("Consider adding direct product links to improve shopping experience.")
    
    # User account links analysis
    account_count = categories.get("account", {}).get("count", 0)
    if account_count > 0:
        insights.append(f"User authentication: {account_count} account-related links found.")
    
    # Support links analysis
    support_count = categories.get("support", {}).get("count", 0)
    if support_count == 0:
        recommendations.append("Add support/help links to assist users with questions or issues.")
    else:
        insights.append(f"Customer support: {support_count} help/support links found.")
    
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
    
    # Content links analysis
    content_count = categories.get("content", {}).get("count", 0)
    if content_count > 10:
        insights.append(f"Rich content: {content_count} blog/article links found.")
    elif content_count > 0:
        insights.append(f"Content available: {content_count} blog/article links.")
    
    # Business links analysis
    business_count = categories.get("business", {}).get("count", 0)
    if business_count > 0:
        insights.append(f"Business pages: {business_count} marketing/business links found.")
    
    # Careers links analysis
    careers_count = categories.get("careers", {}).get("count", 0)
    if careers_count > 0:
        insights.append(f"Hiring opportunities: {careers_count} career/jobs links found.")
    
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
    score = 65  # Base score
    
    # Add points for good practices
    if nav_count >= 5: score += 5
    if social_count > 0: score += 3
    if legal_count > 0: score += 5
    if support_count > 0: score += 3
    if content_count > 5: score += 4
    if ecommerce_count > 0 or product_count > 0: score += 3
    if account_count > 0: score += 2
    if careers_count > 0: score += 2
    if business_count >= 5: score += 3
    if 0.2 <= external_percentage <= 30: score += 7
    if no_anchor_text == 0: score += 5
    
    # Subtract points for issues
    if nav_count == 0: score -= 10
    if legal_count == 0: score -= 5
    if support_count == 0: score -= 3
    if external_percentage > 70: score -= 10
    if no_anchor_text > total_links * 0.2: score -= 10
    
    score = max(0, min(100, score))  # Clamp between 0-100
    
    # Count how many categories have links
    active_categories = sum(1 for cat_data in categories.values() if cat_data.get("count", 0) > 0)
    
    report = {
        "summary": f"Analyzed {total_links} links across {active_categories} categories from {page_domain}",
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