"""
Unified Market Research Tool
Intelligently chooses between Tavily (fast) or deep analysis (thorough) based on query
"""

import os
import json
from typing import Dict, Any
from datetime import datetime
from strands.tools import tool

# Import existing tools
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


@tool
def market_research(query: str, depth: str = "auto") -> Dict[str, Any]:
    """
    Unified market research tool that intelligently chooses the best approach.
    
    Args:
        query: The market research question or topic
        depth: Research depth - "quick", "deep", or "auto" (default)
               - "quick": Fast Tavily search (1-2 seconds)
               - "deep": Comprehensive analysis with AI (10-15 seconds)
               - "auto": Automatically choose based on query complexity
    
    Returns:
        Market research results with competitive data, trends, and insights
    
    Examples:
        - "What are current auto loan rates?" → Quick Tavily search
        - "Analyze the competitive landscape for millennial-focused personal loans" → Deep analysis
        - "Credit card market trends" → Auto-detects (likely quick)
    """
    
    # Determine research approach
    if depth == "auto":
        depth = _determine_research_depth(query)
    
    print(f"🔍 Market Research Mode: {depth.upper()}")
    
    if depth == "quick":
        return _quick_research(query)
    else:
        return _deep_research(query)


def _determine_research_depth(query: str) -> str:
    """
    Intelligently determine if query needs quick or deep research.
    
    Quick research indicators:
    - Simple rate queries
    - Current market data
    - Competitor rates
    
    Deep research indicators:
    - "Analyze", "Compare", "Strategy"
    - Multiple aspects requested
    - Complex competitive analysis
    """
    query_lower = query.lower()
    
    # Keywords that indicate need for deep analysis
    deep_keywords = [
        "analyze", "analysis", "compare", "comparison", "strategy",
        "competitive landscape", "positioning", "opportunities",
        "comprehensive", "detailed", "in-depth", "trends and",
        "market share", "swot", "strengths and weaknesses"
    ]
    
    # Keywords that indicate quick search is sufficient
    quick_keywords = [
        "what are", "current rate", "rates for", "how much",
        "typical rate", "average rate", "going rate"
    ]
    
    # Check for deep analysis indicators
    if any(keyword in query_lower for keyword in deep_keywords):
        return "deep"
    
    # Check for quick search indicators
    if any(keyword in query_lower for keyword in quick_keywords):
        return "quick"
    
    # Default to quick for simple queries
    if len(query.split()) <= 8:
        return "quick"
    
    return "deep"


def _quick_research(query: str) -> Dict[str, Any]:
    """
    Fast market research using Tavily API.
    Best for: Quick rate checks, current market data, simple competitor info
    Speed: 1-2 seconds
    """
    try:
        api_key = os.getenv('TAVILY_API_KEY')
        
        if not api_key or not TAVILY_AVAILABLE or api_key == 'your_tavily_api_key_here':
            print("⚠️ Tavily not available, using fallback data")
            return _fallback_data(query)
        api_key = os.getenv('TAVILY_API_KEY')
        client = TavilyClient(api_key=api_key)
        response = client.search(query, max_results=5, include_answer=True)
        
        # Parse competitive data
        competitors = []
        for result in response.get("results", []):
            content = result.get("content", "")
            title = result.get("title", "")
            
            if any(term in content.lower() for term in ["bank", "credit union", "loan", "rate"]):
                if "%" in content:
                    try:
                        rate_match = content.split("%")[0].split()[-1]
                        rate = f"{float(rate_match)}%"
                        bank_name = title.split(" ")[0] if title else "Financial Institution"
                        competitors.append({
                            "name": bank_name,
                            "rate": rate,
                            "source": result.get("url", "")
                        })
                    except:
                        pass
        
        return {
            "research_type": "quick",
            "query": query,
            "summary": response.get("answer", ""),
            "competitors": competitors[:5],
            "market_trends": _extract_trends(response.get("results", [])),
            "sources": [r.get("url") for r in response.get("results", [])[:3]],
            "real_data": True,
            "timestamp": datetime.now().isoformat(),
            "processing_time": "1-2 seconds"
        }
        
    except Exception as e:
        print(f"⚠️ Quick research failed: {e}")
        return _fallback_data(query)


def _deep_research(query: str) -> Dict[str, Any]:
    """
    Comprehensive market research with AI analysis.
    Best for: Strategic analysis, competitive positioning, complex insights
    Speed: 10-15 seconds
    """
    try:
        # Step 1: Get base data from Tavily
        quick_data = _quick_research(query)
        
        if not BOTO3_AVAILABLE:
            print("⚠️ Bedrock not available, returning quick research only")
            quick_data["research_type"] = "deep (limited)"
            return quick_data
        
        # Step 2: Enhance with AI analysis
        bedrock = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        
        prompt = f"""
        Analyze this market research data for: {query}
        
        Base Data:
        - Summary: {quick_data.get('summary', '')}
        - Competitors: {json.dumps(quick_data.get('competitors', []), indent=2)}
        - Trends: {quick_data.get('market_trends', [])}
        
        Provide a comprehensive analysis including:
        1. **Competitive Landscape**: Key players and their positioning
        2. **Market Opportunities**: Gaps and opportunities for new products
        3. **Pricing Strategy**: Recommended pricing based on competitive data
        4. **Target Segments**: Most attractive customer segments
        5. **Risk Factors**: Potential challenges and risks
        6. **Strategic Recommendations**: 3-5 actionable recommendations
        
        Format as clear, structured insights for a product manager.
        """
        
        response = bedrock.invoke_model(
            modelId=os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001-v1:0'),
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        ai_analysis = result['content'][0]['text']
        
        return {
            "research_type": "deep",
            "query": query,
            "summary": quick_data.get('summary', ''),
            "ai_analysis": ai_analysis,
            "competitors": quick_data.get('competitors', []),
            "market_trends": quick_data.get('market_trends', []),
            "sources": quick_data.get('sources', []),
            "real_data": True,
            "timestamp": datetime.now().isoformat(),
            "processing_time": "10-15 seconds"
        }
        
    except Exception as e:
        print(f"⚠️ Deep research failed: {e}")
        return _quick_research(query)


def _extract_trends(results: list) -> list:
    """Extract market trends from search results"""
    trends = []
    trend_keywords = {
        "digital": "Digital transformation",
        "mobile": "Mobile-first banking",
        "rate": "Rate competition",
        "online": "Online lending growth",
        "fintech": "Fintech disruption",
        "ai": "AI-powered services",
        "personalization": "Personalized offerings"
    }
    
    for result in results:
        content = result.get("content", "").lower()
        for keyword, trend in trend_keywords.items():
            if keyword in content and trend not in trends:
                trends.append(trend)
    
    return trends[:5] if trends else ["Digital banking growth", "Competitive rate environment"]


def _fallback_data(query: str) -> Dict[str, Any]:
    """Fallback data when Tavily is not available"""
    return {
        "research_type": "fallback",
        "query": query,
        "summary": "Using fallback data - Tavily API key not configured",
        "competitors": [
            {"name": "Major Bank", "rate": "6.25%", "source": "fallback"},
            {"name": "Credit Union", "rate": "5.75%", "source": "fallback"},
            {"name": "Online Lender", "rate": "5.99%", "source": "fallback"}
        ],
        "market_trends": [
            "Digital transformation",
            "Rate competition",
            "Mobile-first banking"
        ],
        "sources": [],
        "real_data": False,
        "timestamp": datetime.now().isoformat(),
        "note": "Configure TAVILY_API_KEY in .env for real-time data"
    }


# Convenience functions for explicit control
@tool
def quick_market_research(query: str) -> Dict[str, Any]:
    """Fast market research using Tavily (1-2 seconds). Use for simple rate checks."""
    return market_research(query, depth="quick")


@tool
def deep_market_research(query: str) -> Dict[str, Any]:
    """Comprehensive market research with AI analysis (10-15 seconds). Use for strategic insights."""
    return market_research(query, depth="deep")
