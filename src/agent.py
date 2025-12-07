from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from tools import extract_meta_tags, get_page_speed, analyze_keyword_density, check_broken_links

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