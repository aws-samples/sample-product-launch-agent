from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from lab_helpers.unified_market_research import market_research
from lab_helpers.enhanced_tools import browse_web
from lab_helpers.marketing_tools import create_marketing_poster

# Create single agent with tools
model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    temperature=0.3
)

agent = Agent(
    model=model,
    tools=[market_research, browse_web, create_marketing_poster],
    system_prompt="""You are a financial product launch assistant.
    Use market_research for market analysis, browse_web for competitor research,
    and create_marketing_poster for marketing materials."""
)

# Initialize AgentCore Runtime App
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    """AgentCore Runtime entrypoint - single agent"""
    user_input = payload.get("prompt", "")
    response = agent(user_input)
    return response

if __name__ == "__main__":
    app.run()

