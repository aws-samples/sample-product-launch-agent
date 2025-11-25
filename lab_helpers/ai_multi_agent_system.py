import os
from typing import Dict, Any
from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel
from strands.tools import tool

load_dotenv()

# Import tools from lab_helpers
from lab_helpers.unified_market_research import market_research
from lab_helpers.enhanced_tools import browse_web
from lab_helpers.marketing_tools import create_marketing_poster

# AI-Enhanced Market Research Agent
market_agent = Agent(
    name="AIMarketResearchAgent",
    model=BedrockModel(model_id=os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-3-5-sonnet-20241022-v2:0')),
    system_prompt="""You are an AI-powered Market Research Specialist.
    
    Use market_research for comprehensive market analysis including:
    - Real-time competitive intelligence
    - Market trends and data
    - Pricing analysis
    
    Use browse_web for targeted competitor website research.
    
    Provide comprehensive market analysis with real-time data, competitive rates, and market trends.""",
    tools=[market_research, browse_web]
)

# AI-Enhanced Compliance Agent
compliance_agent = Agent(
    name="AIComplianceAgent", 
    model=BedrockModel(model_id=os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-3-5-sonnet-20241022-v2:0')),
    system_prompt="""You are an AI-powered Compliance Specialist.
    Use browse_web to research regulatory requirements and compliance frameworks for financial products.""",
    tools=[browse_web]
)

# AI-Enhanced Strategy Agent
strategy_agent = Agent(
    name="AIStrategyAgent",
    model=BedrockModel(model_id=os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-3-5-sonnet-20241022-v2:0')),
    system_prompt="""You are an AI-powered Strategy Specialist.
    Use market_research and browse_web to develop strategic insights and competitive positioning.""",
    tools=[market_research, browse_web]
)

# AI-Enhanced Deployment Agent
deployment_agent = Agent(
    name="AIDeploymentAgent",
    model=BedrockModel(model_id=os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-3-5-sonnet-20241022-v2:0')),
    system_prompt="""You are an AI-powered Deployment Specialist.
    Use browse_web to research best practices for product deployment and launch strategies.""",
    tools=[browse_web]
)

# AI-Enhanced Marketing Agent
marketing_agent = Agent(
    name="AIMarketingAgent",
    model=BedrockModel(model_id=os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-3-5-sonnet-20241022-v2:0')),
    system_prompt="""You are an AI-powered Marketing Specialist using Amazon Nova Canvas.
    
    Use create_marketing_poster to generate marketing materials with:
    - Nova Canvas background images
    - Professional PDF layouts
    - Instagram/Google ad styling
    
    Create ONE high-quality marketing poster per request.""",
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
    model=BedrockModel(model_id=os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-3-5-sonnet-20241022-v2:0')),
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
