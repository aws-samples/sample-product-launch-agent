from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel
from scripts.utils import get_ssm_parameter
from bedrock_agentcore.tools.code_interpreter_client import code_session
from bedrock_agentcore.client import MCPClient
from boto3.session import Session
import os

# Import tools from lab_helpers
from lab_helpers.strands_financial_agent import research_market_data
from lab_helpers.enhanced_tools import browse_web
from lab_helpers.marketing_tools import create_marketing_poster
from lab_helpers.lab2_memory import (
    ProductLaunchMemoryHooks,
    memory_client,
    ACTOR_ID,
    SESSION_ID,
)

# Get region for tools
boto_session = Session()
region = boto_session.region_name

MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

SYSTEM_PROMPT = """You are an expert financial product launch assistant.

Available tools:
- research_market_data: Real-time market research using Tavily API
- browse_web: Browse specific websites for detailed information
- research_with_browser: Automated browser for competitor research and live data extraction
- create_marketing_poster: Generate marketing materials with Nova Canvas
- execute_financial_calculation: Run Python code for financial analysis and calculations
- check_compliance_status: Check regulatory compliance (via Gateway)
- get_pm_profile: Get product manager profile information (via Gateway)

Use these tools to help product managers launch financial products successfully."""

# Lab 3ii: Code Interpreter Tool
@tool
def execute_financial_calculation(python_code: str) -> str:
    """
    Execute Python code for financial calculations and analysis.
    
    Args:
        python_code: Python code to execute (calculations, data analysis, modeling)
    
    Returns:
        Execution results including output and any errors
    """
    try:
        with code_session(region=region) as session:
            result = session.execute_code(python_code)
            
            if result.get('isError'):
                error_msg = result.get('content', [{}])[0].get('text', 'Unknown error')
                return f"Error: {error_msg}"
            
            # Extract stdout from structured content
            structured = result.get('structuredContent', {})
            stdout = structured.get('stdout', '')
            stderr = structured.get('stderr', '')
            
            if stderr:
                return f"Output: {stdout}\nWarnings: {stderr}"
            
            return stdout or "Code executed successfully (no output)"
    except Exception as e:
        return f"Error executing code: {str(e)}"

# Lab 3i: Browser Tool
@tool
def research_with_browser(task_description: str, target_url: str = "") -> str:
    """
    Use automated browser to research competitor websites and extract market data.
    
    Args:
        task_description: What to research (e.g., "Find auto loan rates on Bankrate")
        target_url: Optional specific URL to visit (e.g., "https://www.bankrate.com")
    
    Returns:
        Research findings from the browser automation
    """
    try:
        from bedrock_agentcore.tools.browser_client import BrowserClient
        from playwright.sync_api import sync_playwright
        
        client = BrowserClient(region)
        client.start()
        
        ws_url, headers = client.generate_ws_headers()
        
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(ws_url, headers=headers)
            context = browser.contexts[0]
            page = context.new_page()
            page.set_default_timeout(30000)
            
            # Determine URL based on task
            if target_url:
                url = target_url
            elif "bankrate" in task_description.lower():
                url = "https://www.bankrate.com/loans/auto-loans/rates/"
            elif "nerdwallet" in task_description.lower():
                url = "https://www.nerdwallet.com/auto-loans"
            else:
                return "Please specify a target_url or mention a known financial site (bankrate, nerdwallet)"
            
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            
            # Extract text content
            content = page.content()
            text_content = page.inner_text("body")
            
            # Take screenshot for verification
            screenshot_path = f"/tmp/browser_research_{hash(task_description)}.png"
            page.screenshot(path=screenshot_path)
            
            browser.close()
            client.stop()
            
            # Return relevant excerpt (first 2000 chars)
            return f"Research from {url}:\n\n{text_content[:2000]}...\n\nScreenshot saved to: {screenshot_path}"
            
    except Exception as e:
        return f"Browser research failed: {str(e)}. Try using browse_web tool instead."

# Lab1: Create the Bedrock model
model = BedrockModel(model_id=MODEL_ID)

# Lab2: Initialize memory via hooks
memory_id = get_ssm_parameter("/app/productlaunch/agentcore/memory_id")
memory_hooks = ProductLaunchMemoryHooks(
    memory_id, memory_client, ACTOR_ID, SESSION_ID
)

# Lab3: Initialize Gateway MCP client for shared tools
def get_gateway_token() -> str:
    """Get OAuth token for gateway access using client credentials flow"""
    import requests
    
    try:
        client_id = get_ssm_parameter("/app/productlaunch/agentcore/machine_client_id")
        client_secret = get_ssm_parameter("/app/productlaunch/agentcore/client_secret")
        scope = get_ssm_parameter("/app/productlaunch/agentcore/cognito_auth_scope")
        token_url = get_ssm_parameter("/app/productlaunch/agentcore/cognito_token_url")
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
        }
        
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token", "")
    except Exception as e:
        print(f"Failed to get gateway token: {e}")
        return ""

gateway_tools = []
try:
    gateway_id = get_ssm_parameter("/app/productlaunch/agentcore/gateway_id")
    gateway_url = f"https://bedrock-agentcore.{region}.amazonaws.com/gateways/{gateway_id}/mcp"
    
    # Get OAuth token for gateway access
    bearer_token = get_gateway_token()
    
    if bearer_token:
        from strands.tools.mcp import MCPClient
        from mcp.client.streamable_http import streamablehttp_client
        
        mcp_client = MCPClient(
            lambda: streamablehttp_client(
                gateway_url,
                headers={"Authorization": f"Bearer {bearer_token}"},
            )
        )
        gateway_tools = mcp_client.get_tools()
        print(f"✅ Loaded {len(gateway_tools)} tools from Gateway")
    else:
        print("⚠️ No gateway token available")
except Exception as e:
    print(f"⚠️ Gateway tools not available: {e}")
    gateway_tools = []

# Combine all tools
all_tools = [
    research_market_data,
    browse_web,
    research_with_browser,
    create_marketing_poster,
    execute_financial_calculation,
] + gateway_tools

# Create the agent with all product launch tools
agent = Agent(
    model=model,
    tools=all_tools,
    system_prompt=SYSTEM_PROMPT,
    hooks=[memory_hooks],
)

# Initialize the AgentCore Runtime App
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    """AgentCore Runtime entrypoint function"""
    user_input = payload.get("prompt", "")
    response = agent(user_input)
    return response.message["content"][0]["text"]

if __name__ == "__main__":
    app.run()
