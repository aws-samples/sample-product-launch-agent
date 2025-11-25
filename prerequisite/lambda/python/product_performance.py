import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError
import logging

# Setting logger
logging.basicConfig(
    format="[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb")
ssm_client = boto3.client("ssm")

# Get product performance table name from Parameter Store
try:
    performance_table = ssm_client.get_parameter(
        Name="/app/productlaunch/dynamodb/performance_table_name", WithDecryption=False
    )
    performance_table_name = performance_table["Parameter"]["Value"]
except:
    # Fallback for demo/testing
    performance_table_name = "ProductLaunchPerformance"


def ensure_performance_table_exists():
    """Create the DynamoDB performance table if it doesn't exist."""
    try:
        table = dynamodb.Table(performance_table_name)
        table.load()
        return table
    except ClientError as e:
        # Return None if table doesn't exist - we'll use mock data
        logger.warning(f"Performance table not found: {e}")
        return None


def get_mock_performance_data(product_id: str) -> dict:
    """Return mock product performance data for demonstration."""
    
    performance_db = {
        "AUTO_LOAN_2023": {
            "product_name": "Auto Loan Premium 2023",
            "launch_date": "2023-03-15",
            "margin": "15.2%",
            "market_share": "8.3%",
            "customer_satisfaction": 4.2,
            "revenue_ytd": "$45.2M",
            "active_accounts": 12450,
            "default_rate": "2.1%",
            "strategic_vision": "Premium auto lending with digital-first experience targeting millennials and Gen Z",
            "key_features": ["Digital application", "Same-day approval", "Competitive rates", "Mobile app management"],
            "target_demographics": ["Ages 25-45", "Income $50K+", "Good credit (650+)"],
            "competitive_advantages": ["Fast approval process", "Lower rates than traditional banks", "Superior mobile experience"]
        },
        "PERSONAL_LOAN_PRIME": {
            "product_name": "Personal Loan Prime",
            "launch_date": "2023-06-01",
            "margin": "12.8%",
            "market_share": "5.7%",
            "customer_satisfaction": 4.0,
            "revenue_ytd": "$28.7M",
            "active_accounts": 8920,
            "default_rate": "3.2%",
            "strategic_vision": "Debt consolidation and major purchase financing for prime customers",
            "key_features": ["Fixed rates", "No prepayment penalty", "Flexible terms", "Online management"],
            "target_demographics": ["Ages 30-55", "Income $60K+", "Excellent credit (720+)"],
            "competitive_advantages": ["Transparent pricing", "Quick funding", "Excellent customer service"]
        },
        "CREDIT_CARD_REWARDS": {
            "product_name": "Rewards Credit Card",
            "launch_date": "2023-09-10",
            "margin": "18.5%",
            "market_share": "3.2%",
            "customer_satisfaction": 4.4,
            "revenue_ytd": "$22.1M",
            "active_accounts": 15680,
            "default_rate": "1.8%",
            "strategic_vision": "Premium rewards card for high-spending customers with travel and cashback benefits",
            "key_features": ["2% cashback", "Travel rewards", "No annual fee", "Mobile wallet integration"],
            "target_demographics": ["Ages 25-50", "Income $75K+", "Excellent credit (740+)"],
            "competitive_advantages": ["High rewards rate", "No annual fee", "Premium customer service"]
        }
    }
    
    return performance_db.get(product_id, {
        "product_name": f"Product {product_id}",
        "launch_date": "2023-01-01",
        "margin": "10.0%",
        "market_share": "2.5%",
        "customer_satisfaction": 3.8,
        "revenue_ytd": "$15.0M",
        "active_accounts": 5000,
        "default_rate": "2.5%",
        "strategic_vision": "Standard financial product offering",
        "key_features": ["Competitive rates", "Online application", "Customer support"],
        "target_demographics": ["General market"],
        "competitive_advantages": ["Reliable service", "Competitive pricing"]
    })


def get_product_performance(product_id: str, include_vision: bool = False) -> str:
    """
    Get existing product performance data from enterprise analytics.

    Args:
        product_id (str): Product identifier (e.g., AUTO_LOAN_2023, PERSONAL_LOAN_PRIME).
        include_vision (bool): Include strategic vision and roadmap information.

    Returns:
        str: Formatted product performance data including margins, market share, satisfaction, etc.
    """
    logger.info(
        json.dumps(
            {
                "product_id": product_id,
                "include_vision": include_vision,
                "timestamp": datetime.now().isoformat(),
            },
            indent=2,
        )
    )

    try:
        table = ensure_performance_table_exists()
        
        # Try to get from DynamoDB first
        if table:
            try:
                response = table.get_item(
                    Key={"product_id": product_id}
                )
                
                if "Item" in response:
                    performance_data = response["Item"]
                else:
                    # Use mock data if not found in DB
                    performance_data = get_mock_performance_data(product_id)
            except:
                performance_data = get_mock_performance_data(product_id)
        else:
            # Use mock data if table doesn't exist
            performance_data = get_mock_performance_data(product_id)

        # Format performance information
        performance_info = [
            "📊 Product Performance Dashboard",
            "=" * 50,
            f"🏦 Product: {performance_data.get('product_name', product_id)}",
            f"📅 Launch Date: {performance_data.get('launch_date', 'N/A')}",
            "",
            "💰 Financial Metrics:",
            f"   • Profit Margin: {performance_data.get('margin', 'N/A')}",
            f"   • Market Share: {performance_data.get('market_share', 'N/A')}",
            f"   • Revenue YTD: {performance_data.get('revenue_ytd', 'N/A')}",
            f"   • Active Accounts: {performance_data.get('active_accounts', 'N/A'):,}",
            f"   • Default Rate: {performance_data.get('default_rate', 'N/A')}",
            "",
            "😊 Customer Metrics:",
            f"   • Satisfaction Score: {performance_data.get('customer_satisfaction', 'N/A')}/5.0",
        ]
        
        # Add key features
        if "key_features" in performance_data:
            performance_info.extend([
                "",
                "🔑 Key Features:",
            ])
            for feature in performance_data["key_features"]:
                performance_info.append(f"   • {feature}")
        
        # Add target demographics
        if "target_demographics" in performance_data:
            performance_info.extend([
                "",
                "🎯 Target Demographics:",
            ])
            for demo in performance_data["target_demographics"]:
                performance_info.append(f"   • {demo}")
        
        # Add competitive advantages
        if "competitive_advantages" in performance_data:
            performance_info.extend([
                "",
                "🏆 Competitive Advantages:",
            ])
            for advantage in performance_data["competitive_advantages"]:
                performance_info.append(f"   • {advantage}")
        
        # Include strategic vision if requested
        if include_vision and "strategic_vision" in performance_data:
            performance_info.extend([
                "",
                "🎯 Strategic Vision:",
                f"   {performance_data['strategic_vision']}",
            ])
        
        performance_info.extend([
            "",
            "📈 Insights for New Product Launch:",
            "   • Leverage successful features from this product",
            "   • Consider similar target demographics",
            "   • Apply lessons learned from performance metrics",
            "   • Maintain or improve customer satisfaction levels",
        ])

        logger.info(json.dumps(performance_data, indent=2, default=str))
        return "\n".join(performance_info)

    except Exception as e:
        logger.error(f"Product performance error: {str(e)}")
        return f"❌ Failed to get product performance: {str(e)}"
