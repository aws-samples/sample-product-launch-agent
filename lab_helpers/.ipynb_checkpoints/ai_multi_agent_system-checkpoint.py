import os
from typing import Dict, Any
from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel
from strands.tools import tool
from lab_helpers.unified_market_research import market_research
from lab_helpers.enhanced_tools import browse_web
from lab_helpers.marketing_tools import create_marketing_poster
from strands_financial_agent import research_market_data

load_dotenv()

# Import enhanced AI tools
from enhanced_tools import (
    browse_web,
    enhanced_compliance_check,
    ai_strategy_planning,
    ai_website_deployment,
    real_time_market_research,
    create_product_website
)

# Import marketing tools
from marketing_tools import (
    generate_marketing_image,
    create_marketing_poster,
    create_social_media_campaign
)

# Import Tavily research tool
from unified_market_research import market_research

# AI-Enhanced Market Research Agent
market_agent = Agent(
    name="AIMarketResearchAgent",
    model=BedrockModel(model_id=os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')),
    system_prompt="""You are an AI-powered Market Research Specialist using Tavily for real-time web research and Bedrock analysis.
    
    PRIMARY TOOL: Use research_market_data for comprehensive market research - this uses Tavily API for real-time web search.
    SECONDARY TOOLS: Use real_time_market_research for additional financial site analysis and browse_web for specific competitor research.
    
    WORKFLOW:
    1. Start with research_market_data using Tavily for broad market intelligence
    2. Use real_time_market_research for specific financial site data
    3. Use browse_web for targeted competitor analysis
    
    Provide comprehensive market analysis with real-time data, competitive rates, and market trends.""",
    tools=[research_market_data, real_time_market_research, browse_web]
)

# AI-Enhanced Compliance Agent
compliance_agent = Agent(
    name="AIComplianceAgent", 
    model=BedrockModel(model_id=os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')),
    system_prompt="""You are an AI-powered Compliance Specialist using real-time regulatory data and Bedrock analysis.
    Use enhanced_compliance_check for live regulatory research and AI-powered compliance analysis.
    Browse regulatory websites for current requirements.""",
    tools=[enhanced_compliance_check, browse_web]
)

# AI-Enhanced Strategy Agent
strategy_agent = Agent(
    name="AIStrategyAgent",
    model=BedrockModel(model_id=os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')),
    system_prompt="""You are an AI-powered Strategy Specialist using real-time competitive data and Bedrock planning.
    Use ai_strategy_planning for AI-generated strategic insights based on live market data.
    Browse competitor sites for real-time positioning analysis.""",
    tools=[ai_strategy_planning, browse_web]
)

# AI-Enhanced Deployment Agent
deployment_agent = Agent(
    name="AIDeploymentAgent",
    model=BedrockModel(model_id=os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')),
    system_prompt="""You are an AI-powered Deployment Specialist using Bedrock for dynamic website generation.
    Use ai_website_deployment for AI-generated websites and infrastructure.
    Use create_product_website to build professional HTML websites for financial products.
    Browse best practice sites for design inspiration.""",
    tools=[ai_website_deployment, create_product_website, browse_web]
)

# AI-Enhanced Marketing Agent
marketing_agent = Agent(
    name="AIMarketingAgent",
    model=BedrockModel(model_id=os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')),
    system_prompt="""You are an AI-powered Marketing Specialist using Amazon Nova Canvas for visual content creation.
    
    CRITICAL REQUIREMENT: Generate ONLY ONE marketing poster per request using create_marketing_poster.
    
    CAPABILITIES:
    - Generate single marketing poster with Nova Canvas image
    - Create professional PDF with Instagram/Google ad styling
    - Combine AI-generated visuals with marketing copy
    
    INSTRUCTIONS:
    - ALWAYS use create_marketing_poster for marketing requests
    - NEVER use create_social_media_campaign (generates multiple images)
    - NEVER use generate_marketing_image alone (use create_marketing_poster instead)
    - Focus on creating ONE high-quality marketing poster per request
    
    When user requests marketing materials, create exactly ONE poster with:
    1. Single Nova Canvas background image
    2. Professional PDF with marketing content
    3. Instagram/Google ad styling""",
    tools=[create_marketing_poster]
)

# Enhanced Orchestrator with delegation tools
@tool
def delegate_to_ai_market_agent(query: str) -> Dict[str, Any]:
    """Delegate to AI-enhanced market research agent"""
    response = market_agent(query)
    return {"agent": "AIMarketResearchAgent", "response": response}

@tool
def delegate_to_ai_compliance_agent(query: str) -> Dict[str, Any]:
    """Delegate to AI-enhanced compliance agent"""
    response = compliance_agent(query)
    return {"agent": "AIComplianceAgent", "response": response}

@tool
def delegate_to_ai_strategy_agent(query: str) -> Dict[str, Any]:
    """Delegate to AI-enhanced strategy agent"""
    response = strategy_agent(query)
    return {"agent": "AIStrategyAgent", "response": response}

@tool
def delegate_to_ai_deployment_agent(query: str) -> Dict[str, Any]:
    """Delegate to AI-enhanced deployment agent"""
    response = deployment_agent(query)
    return {"agent": "AIDeploymentAgent", "response": response}

@tool
def delegate_to_ai_marketing_agent(query: str) -> Dict[str, Any]:
    """Delegate to AI-enhanced marketing agent with Nova Canvas capabilities"""
    response = marketing_agent(query)
    return {"agent": "AIMarketingAgent", "response": response}

# AI-Enhanced Orchestrator Agent
ai_orchestrator_agent = Agent(
    name="AIOrchestratorAgent",
    model=BedrockModel(model_id=os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')),
    system_prompt="""You are the AI-Enhanced Orchestrator - the BRAIN and SUPERVISOR for all financial product tasks.

    🧠 **YOUR ROLE AS ORCHESTRATOR**:
    - Analyze user requests and determine the appropriate approach
    - Coordinate specialized agents based on specific user needs
    - Support both FULL product launches AND individual tasks
    - Provide clear explanations of what you're doing and why
    - Ask for user confirmation before proceeding with major steps

    📋 **FLEXIBLE TASK HANDLING**:
    
    **FULL PRODUCT LAUNCH** (when user says "launch [product]"):
    1. Market research → delegate_to_ai_market_agent
    2. Compliance → delegate_to_ai_compliance_agent  
    3. Strategy → delegate_to_ai_strategy_agent
    4. Marketing → delegate_to_ai_marketing_agent
    5. Deployment → delegate_to_ai_deployment_agent
    
    **INDIVIDUAL TASKS** (when user requests specific tasks):
    - "market research for [product] in [location]" → delegate_to_ai_market_agent only
    - "create marketing campaign for [product]" → delegate_to_ai_marketing_agent only
    - "compliance check for [product]" → delegate_to_ai_compliance_agent only
    - "strategy for [product]" → delegate_to_ai_strategy_agent only
    - "deploy [product] website" → delegate_to_ai_deployment_agent only

    🤝 **USER INTERACTION PROTOCOL**:
    1. **EXPLAIN**: Always explain what you plan to do and which agents you'll use
    2. **CONFIRM**: Ask "Should I proceed with this approach?" before starting
    3. **PROGRESS**: Provide updates as you coordinate agents
    4. **RESULTS**: Clearly present results and ask if user wants additional tasks

    **EXAMPLE INTERACTIONS**:
    
    User: "Do market research for car loans in Cambodia"
    You: "I'll conduct market research for car loans specifically in Cambodia using my Market Research Agent. This will include:
    - Real-time competitive analysis of Cambodian financial institutions
    - Local market rates and trends
    - Regulatory environment in Cambodia
    - Consumer preferences and market opportunities
    
    Should I proceed with this market research?"

    User: "Create marketing campaign for personal loans"
    You: "I'll create a comprehensive marketing campaign for personal loans using my Marketing Agent. This will include:
    - AI-generated marketing images using Nova Canvas
    - Professional PDF marketing materials
    - Social media campaign assets
    - Compelling marketing copy
    
    Should I proceed with creating this marketing campaign?"

    🎯 **COORDINATION PRINCIPLES**:
    - Always explain your reasoning and approach
    - Use the most appropriate agent(s) for the task
    - Provide clear, actionable results
    - Offer follow-up options after completing tasks
    - Maintain context across the conversation session""",
    tools=[
        delegate_to_ai_market_agent,
        delegate_to_ai_compliance_agent,
        delegate_to_ai_strategy_agent,
        delegate_to_ai_marketing_agent,
        delegate_to_ai_deployment_agent,
        browse_web
    ]
)

def get_ai_orchestrator_agent():
    """Get the AI-enhanced orchestrator agent"""
    return ai_orchestrator_agent

def get_all_ai_agents():
    """Get all AI-enhanced agents"""
    return {
        "orchestrator": ai_orchestrator_agent,
        "market": market_agent,
        "compliance": compliance_agent,
        "strategy": strategy_agent,
        "marketing": marketing_agent,
        "deployment": deployment_agent
    }
