from bedrock_agentcore.runtime import BedrockAgentCoreApp
from lab_helpers.ai_multi_agent_system import get_ai_orchestrator_agent

# Get the multi-agent orchestrator
orchestrator = get_ai_orchestrator_agent()

# Initialize AgentCore Runtime App
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    """AgentCore Runtime entrypoint - routes to multi-agent orchestrator"""
    user_input = payload.get("prompt", "")
    response = orchestrator(user_input)
    return response

if __name__ == "__main__":
    app.run()
