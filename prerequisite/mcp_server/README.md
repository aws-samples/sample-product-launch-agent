# Mastercard MCP Server (Mock)

This is a mock MCP server that simulates Mastercard's financial data APIs for demonstration purposes.

## Features

### Tools Provided:

1. **get_fraud_prevention_tools** - Information about Mastercard's fraud prevention suite
   - Decision Intelligence
   - NuData Security
   - RiskRecon
   - Ethoca

2. **get_market_intelligence** - Real-time market data for financial products
   - Average rates
   - Market size
   - Growth rates
   - Competitive landscape
   - Customer segments

3. **get_transaction_insights** - Transaction patterns and spending insights
   - Demographic analysis
   - Spending categories
   - Digital preferences
   - Mobile usage patterns

## Installation

```bash
cd labs/prerequisite/mcp_server
pip install -r requirements.txt
```

## Running Locally

```bash
python mastercard_mcp.py
```

## Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python mastercard_mcp.py
```

## Integration with AgentCore Gateway

### Option 1: Run as Local Process

```python
# In your notebook or script
import subprocess
import json

# Start the MCP server
process = subprocess.Popen(
    ["python", "labs/prerequisite/mcp_server/mastercard_mcp.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Connect via stdio
from mcp.client.stdio import stdio_client

async with stdio_client(process) as (read, write):
    # Use the MCP client
    pass
```

### Option 2: Add as Gateway Target (External MCP)

```python
# Create external MCP target in Gateway
external_mcp_config = {
    "mcp": {
        "externalServer": {
            "serverUrl": "http://your-mcp-server-endpoint",
            "authConfig": {
                "type": "API_KEY",
                "apiKey": "your-api-key"
            }
        }
    }
}

gateway_client.create_gateway_target(
    gatewayIdentifier=gateway_id,
    name="MastercardMCP",
    description="Mastercard Financial Data MCP Server",
    targetConfiguration=external_mcp_config,
    credentialProviderConfigurations=[{
        "credentialProviderType": "GATEWAY_IAM_ROLE"
    }]
)
```

### Option 3: Deploy as Lambda Function

Package the MCP server as a Lambda function and add it as another Lambda target to your Gateway.

## Production Considerations

In production, replace this mock server with:

1. **Actual Mastercard API Integration**
   - Get Mastercard Developer credentials
   - Use official Mastercard SDKs
   - Implement proper authentication

2. **Deploy to AWS**
   - Lambda function with MCP protocol
   - ECS/Fargate container
   - EC2 instance with proper networking

3. **Security**
   - API key management via Secrets Manager
   - VPC endpoints for private connectivity
   - Rate limiting and throttling

4. **Monitoring**
   - CloudWatch metrics
   - X-Ray tracing
   - Error alerting

## Example Queries

```python
# Get fraud prevention tools
result = await client.call_tool(
    "get_fraud_prevention_tools",
    {"tool_name": "Decision Intelligence"}
)

# Get market intelligence
result = await client.call_tool(
    "get_market_intelligence",
    {
        "product_type": "auto_loan",
        "data_points": ["rates", "competitors"]
    }
)

# Get transaction insights
result = await client.call_tool(
    "get_transaction_insights",
    {
        "segment": "millennials",
        "category": "automotive"
    }
)
```

## Resources

- [Mastercard Developers](https://developer.mastercard.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [AgentCore Gateway Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)
