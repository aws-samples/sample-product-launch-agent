#!/usr/bin/env python3
"""
Mock Mastercard MCP Server for demonstration purposes.
In production, this would connect to actual Mastercard APIs.
"""

import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Mock Mastercard data
MASTERCARD_FRAUD_TOOLS = {
    "Decision Intelligence": {
        "description": "AI-powered fraud detection using machine learning",
        "features": ["Real-time scoring", "Behavioral analytics", "Pattern recognition"],
        "use_case": "Transaction monitoring and fraud prevention"
    },
    "NuData Security": {
        "description": "Passive biometrics and behavioral analytics",
        "features": ["Device fingerprinting", "Behavioral biometrics", "Account takeover prevention"],
        "use_case": "Account security and authentication"
    },
    "RiskRecon": {
        "description": "Third-party risk management and vendor security",
        "features": ["Vendor risk scoring", "Security ratings", "Continuous monitoring"],
        "use_case": "Supply chain security"
    },
    "Ethoca": {
        "description": "Collaboration network for fraud and dispute resolution",
        "features": ["Chargeback prevention", "Fraud alerts", "Merchant collaboration"],
        "use_case": "Dispute management"
    }
}

MARKET_DATA = {
    "auto_loan": {
        "average_rate": "6.5%",
        "market_size": "$1.2T",
        "growth_rate": "3.2%",
        "top_competitors": ["Chase", "Bank of America", "Wells Fargo"],
        "customer_segments": ["Prime (720+)", "Near-prime (650-719)", "Subprime (<650)"]
    },
    "personal_loan": {
        "average_rate": "11.5%",
        "market_size": "$180B",
        "growth_rate": "8.5%",
        "top_competitors": ["SoFi", "LendingClub", "Prosper"],
        "customer_segments": ["Debt consolidation", "Home improvement", "Major purchases"]
    },
    "credit_card": {
        "average_rate": "19.5%",
        "market_size": "$4.2T",
        "growth_rate": "5.1%",
        "top_competitors": ["Chase", "American Express", "Citi"],
        "customer_segments": ["Rewards seekers", "Balance transferers", "Credit builders"]
    }
}


# Create MCP server
app = Server("mastercard-financial-data")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Mastercard tools."""
    return [
        Tool(
            name="get_fraud_prevention_tools",
            description="Get information about Mastercard's fraud prevention and security tools",
            inputSchema={
                "type": "object",
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "description": "Specific tool name (optional). Options: Decision Intelligence, NuData Security, RiskRecon, Ethoca",
                        "enum": ["Decision Intelligence", "NuData Security", "RiskRecon", "Ethoca", "all"]
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_market_intelligence",
            description="Get real-time market intelligence for financial products including rates, market size, and competitive landscape",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_type": {
                        "type": "string",
                        "description": "Type of financial product",
                        "enum": ["auto_loan", "personal_loan", "credit_card"]
                    },
                    "data_points": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["rates", "market_size", "growth", "competitors", "segments"]
                        },
                        "description": "Specific data points to retrieve"
                    }
                },
                "required": ["product_type"]
            }
        ),
        Tool(
            name="get_transaction_insights",
            description="Get transaction patterns and spending insights for customer segmentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "segment": {
                        "type": "string",
                        "description": "Customer segment to analyze",
                        "enum": ["millennials", "gen_z", "gen_x", "boomers", "all"]
                    },
                    "category": {
                        "type": "string",
                        "description": "Spending category",
                        "enum": ["automotive", "retail", "travel", "dining", "all"]
                    }
                },
                "required": ["segment"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    
    if name == "get_fraud_prevention_tools":
        tool_name = arguments.get("tool_name", "all")
        
        if tool_name == "all" or not tool_name:
            # Return all tools
            result = "🛡️ Mastercard Fraud Prevention Tools\n"
            result += "=" * 50 + "\n\n"
            
            for tool, details in MASTERCARD_FRAUD_TOOLS.items():
                result += f"**{tool}**\n"
                result += f"Description: {details['description']}\n"
                result += f"Key Features:\n"
                for feature in details['features']:
                    result += f"  • {feature}\n"
                result += f"Use Case: {details['use_case']}\n\n"
            
            result += "\n💡 Integration Options:\n"
            result += "  • REST API integration\n"
            result += "  • SDK libraries (Java, Python, Node.js)\n"
            result += "  • Webhook notifications\n"
            result += "  • Real-time scoring endpoints\n"
            
        elif tool_name in MASTERCARD_FRAUD_TOOLS:
            # Return specific tool
            details = MASTERCARD_FRAUD_TOOLS[tool_name]
            result = f"🛡️ {tool_name}\n"
            result += "=" * 50 + "\n\n"
            result += f"Description: {details['description']}\n\n"
            result += "Key Features:\n"
            for feature in details['features']:
                result += f"  • {feature}\n"
            result += f"\nUse Case: {details['use_case']}\n"
        else:
            result = f"❌ Tool '{tool_name}' not found. Available tools: {', '.join(MASTERCARD_FRAUD_TOOLS.keys())}"
        
        return [TextContent(type="text", text=result)]
    
    elif name == "get_market_intelligence":
        product_type = arguments.get("product_type")
        data_points = arguments.get("data_points", ["all"])
        
        if product_type not in MARKET_DATA:
            return [TextContent(
                type="text",
                text=f"❌ Product type '{product_type}' not found. Available: {', '.join(MARKET_DATA.keys())}"
            )]
        
        data = MARKET_DATA[product_type]
        result = f"📊 Market Intelligence: {product_type.replace('_', ' ').title()}\n"
        result += "=" * 50 + "\n\n"
        
        if "all" in data_points or "rates" in data_points:
            result += f"💰 Average Rate: {data['average_rate']}\n"
        
        if "all" in data_points or "market_size" in data_points:
            result += f"📈 Market Size: {data['market_size']}\n"
        
        if "all" in data_points or "growth" in data_points:
            result += f"📊 Growth Rate: {data['growth_rate']}\n"
        
        if "all" in data_points or "competitors" in data_points:
            result += f"\n🏆 Top Competitors:\n"
            for comp in data['top_competitors']:
                result += f"  • {comp}\n"
        
        if "all" in data_points or "segments" in data_points:
            result += f"\n🎯 Customer Segments:\n"
            for seg in data['customer_segments']:
                result += f"  • {seg}\n"
        
        result += "\n📅 Data as of: November 2024\n"
        result += "Source: Mastercard Market Intelligence Platform\n"
        
        return [TextContent(type="text", text=result)]
    
    elif name == "get_transaction_insights":
        segment = arguments.get("segment", "all")
        category = arguments.get("category", "all")
        
        result = f"💳 Transaction Insights\n"
        result += "=" * 50 + "\n\n"
        result += f"Segment: {segment.replace('_', ' ').title()}\n"
        result += f"Category: {category.replace('_', ' ').title()}\n\n"
        
        # Mock insights based on segment
        insights = {
            "millennials": {
                "avg_transaction": "$87",
                "frequency": "12 transactions/month",
                "top_categories": ["Dining", "Travel", "Online Shopping"],
                "digital_preference": "95%",
                "mobile_usage": "78%"
            },
            "gen_z": {
                "avg_transaction": "$52",
                "frequency": "18 transactions/month",
                "top_categories": ["Online Shopping", "Entertainment", "Food Delivery"],
                "digital_preference": "98%",
                "mobile_usage": "92%"
            },
            "gen_x": {
                "avg_transaction": "$124",
                "frequency": "15 transactions/month",
                "top_categories": ["Retail", "Automotive", "Home Improvement"],
                "digital_preference": "82%",
                "mobile_usage": "65%"
            },
            "boomers": {
                "avg_transaction": "$156",
                "frequency": "10 transactions/month",
                "top_categories": ["Healthcare", "Travel", "Retail"],
                "digital_preference": "68%",
                "mobile_usage": "45%"
            }
        }
        
        if segment in insights:
            data = insights[segment]
            result += f"Average Transaction: {data['avg_transaction']}\n"
            result += f"Transaction Frequency: {data['frequency']}\n"
            result += f"Digital Preference: {data['digital_preference']}\n"
            result += f"Mobile Usage: {data['mobile_usage']}\n\n"
            result += "Top Categories:\n"
            for cat in data['top_categories']:
                result += f"  • {cat}\n"
        else:
            result += "Showing aggregated data across all segments\n"
            result += "Average Transaction: $105\n"
            result += "Transaction Frequency: 14 transactions/month\n"
            result += "Digital Preference: 86%\n"
        
        result += "\n📊 Insights for Product Launch:\n"
        result += "  • Target digital-first customers for better engagement\n"
        result += "  • Mobile app is critical for younger demographics\n"
        result += "  • Consider category-specific rewards programs\n"
        
        return [TextContent(type="text", text=result)]
    
    else:
        return [TextContent(
            type="text",
            text=f"❌ Unknown tool: {name}"
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
