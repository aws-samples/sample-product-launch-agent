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

# Get compliance table name from Parameter Store
try:
    compliance_table = ssm_client.get_parameter(
        Name="/app/productlaunch/dynamodb/compliance_table_name", WithDecryption=False
    )
    compliance_table_name = compliance_table["Parameter"]["Value"]
except:
    # Fallback for demo/testing
    compliance_table_name = "ProductLaunchCompliance"


def ensure_compliance_table_exists():
    """Create the DynamoDB compliance table if it doesn't exist."""
    try:
        table = dynamodb.Table(compliance_table_name)
        table.load()
        return table
    except ClientError as e:
        # Return None if table doesn't exist - we'll use mock data
        logger.warning(f"Compliance table not found: {e}")
        return None


def get_mock_compliance_data(product_type: str, region: str) -> dict:
    """Return mock compliance data for demonstration."""
    
    compliance_db = {
        "auto_loan": {
            "US": {
                "federal_regulations": ["Truth in Lending Act (TILA)", "Fair Credit Reporting Act (FCRA)", "Equal Credit Opportunity Act (ECOA)"],
                "state_requirements": ["State lending license", "Interest rate caps", "Consumer protection laws"],
                "required_licenses": ["Consumer lending license", "Auto finance license", "NMLS registration"],
                "compliance_timeline": "4-6 weeks"
            },
            "US-CA": {
                "federal_regulations": ["TILA", "FCRA", "ECOA"],
                "state_requirements": ["California Finance Lenders Law", "CA interest rate caps (max 36% APR)", "CA Consumer Privacy Act (CCPA)"],
                "required_licenses": ["California Finance Lenders License", "NMLS registration"],
                "compliance_timeline": "6-8 weeks"
            }
        },
        "personal_loan": {
            "US": {
                "federal_regulations": ["TILA", "FCRA", "ECOA", "UDAAP"],
                "state_requirements": ["State lending licenses", "Interest rate regulations", "Collection practices"],
                "required_licenses": ["Consumer lending license", "Personal loan license", "NMLS registration"],
                "compliance_timeline": "4-6 weeks"
            }
        },
        "credit_card": {
            "US": {
                "federal_regulations": ["CARD Act", "TILA", "FCRA", "ECOA"],
                "state_requirements": ["State banking regulations", "Consumer protection"],
                "required_licenses": ["Credit card issuer license", "Banking license", "Payment processor registration"],
                "compliance_timeline": "8-12 weeks"
            }
        }
    }
    
    # Get compliance data
    product_data = compliance_db.get(product_type, compliance_db["auto_loan"])
    region_data = product_data.get(region, product_data.get("US", {}))
    
    return region_data


def check_regulatory_compliance(product_type: str, region: str) -> str:
    """
    Check regulatory compliance requirements for financial products.

    Args:
        product_type (str): Type of financial product (auto_loan, personal_loan, credit_card).
        region (str): Country or state code (US, US-CA, UK, etc.).

    Returns:
        str: Formatted compliance information including regulations, licenses, and timeline.
    """
    logger.info(
        json.dumps(
            {
                "product_type": product_type,
                "region": region,
                "timestamp": datetime.now().isoformat(),
            },
            indent=2,
        )
    )

    try:
        table = ensure_compliance_table_exists()
        
        # Try to get from DynamoDB first
        if table:
            try:
                response = table.get_item(
                    Key={"product_type": product_type, "region": region}
                )
                
                if "Item" in response:
                    compliance_data = response["Item"]
                else:
                    # Use mock data if not found in DB
                    compliance_data = get_mock_compliance_data(product_type, region)
            except:
                compliance_data = get_mock_compliance_data(product_type, region)
        else:
            # Use mock data if table doesn't exist
            compliance_data = get_mock_compliance_data(product_type, region)

        # Format compliance information
        product_name = product_type.replace('_', ' ').title()
        region_name = region.replace('-', ' - ')
        
        compliance_info = [
            "📋 Regulatory Compliance Requirements",
            "=" * 50,
            f"🏦 Product Type: {product_name}",
            f"🌎 Region: {region_name}",
            "",
            "📜 Federal Regulations:",
        ]
        
        for reg in compliance_data.get("federal_regulations", []):
            compliance_info.append(f"   • {reg}")
        
        compliance_info.extend([
            "",
            "🏛️ State/Regional Requirements:",
        ])
        
        for req in compliance_data.get("state_requirements", []):
            compliance_info.append(f"   • {req}")
        
        compliance_info.extend([
            "",
            "📝 Required Licenses:",
        ])
        
        for lic in compliance_data.get("required_licenses", []):
            compliance_info.append(f"   • {lic}")
        
        compliance_info.extend([
            "",
            f"⏱️ Compliance Timeline: {compliance_data.get('compliance_timeline', '4-6 weeks')}",
            "",
            "✅ Next Steps:",
            "   1. Legal team review of regulatory requirements",
            "   2. Compliance documentation preparation",
            "   3. Regulatory filing submissions",
            "   4. Internal compliance training",
        ])

        logger.info(json.dumps(compliance_data, indent=2, default=str))
        return "\n".join(compliance_info)

    except Exception as e:
        logger.error(f"Compliance check error: {str(e)}")
        return f"❌ Failed to check compliance: {str(e)}"
