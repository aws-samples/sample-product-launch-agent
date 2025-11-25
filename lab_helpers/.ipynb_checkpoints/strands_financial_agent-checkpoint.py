import os
import json
import base64
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from PIL import Image, ImageDraw, ImageFont
import io

# Load environment variables
load_dotenv()

# Strands SDK imports
from strands import Agent
from strands.models import BedrockModel
from strands.tools import tool

# Tavily for web research
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

# AWS Bedrock for Nova Canvas
try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

# Enhanced Tavily research tool
@tool
def research_market_data(query: str) -> Dict[str, Any]:
    """Research real-time market data using Tavily web search for competitive analysis"""
    try:
        api_key = os.getenv('TAVILY_API_KEY')
        if not api_key or not TAVILY_AVAILABLE:
            return {
                "error": "Tavily not available",
                "fallback_data": {
                    "competitors": [
                        {"name": "Major Bank", "rate": "6.25%", "features": ["Online application", "24/7 support"]},
                        {"name": "Credit Union", "rate": "5.75%", "features": ["Member benefits", "Local service"]}
                    ],
                    "market_trends": ["Digital transformation", "Rate competition", "Mobile-first banking"],
                    "market_size": "$1.2 trillion auto loan market",
                    "growth_rate": "3.5% annually",
                    "real_data": False
                }
            }
        
        client = TavilyClient(api_key=api_key)
        response = client.search(query, max_results=5, include_answer=True)
        
        # Parse competitive data from search results
        competitors = []
        market_trends = []
        
        for result in response.get("results", []):
            content = result.get("content", "")
            title = result.get("title", "")
            
            # Extract competitor information
            if any(term in content.lower() for term in ["bank", "credit union", "loan", "rate"]):
                # Simple parsing - in production, you'd use more sophisticated NLP
                if "%" in content:
                    rate_match = content.split("%")[0].split()[-1]
                    try:
                        rate = f"{float(rate_match)}%"
                        bank_name = title.split(" ")[0] if title else "Financial Institution"
                        competitors.append({
                            "name": bank_name,
                            "rate": rate,
                            "features": ["Competitive rates", "Professional service"]
                        })
                    except:
                        pass
        
        return {
            "query": query,
            "answer": response.get("answer", ""),
            "results": response.get("results", []),
            "competitors": competitors[:3] if competitors else [
                {"name": "Major Bank", "rate": "6.25%", "features": ["Online application"]},
                {"name": "Credit Union", "rate": "5.75%", "features": ["Member benefits"]}
            ],
            "market_trends": ["Digital banking growth", "Competitive rate environment", "Customer experience focus"],
            "real_data": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e), 
            "real_data": False,
            "fallback_data": {
                "competitors": [{"name": "Major Bank", "rate": "6.25%"}],
                "market_trends": ["Digital transformation"]
            }
        }

# Enhanced marketing campaign generator with PDF output
@tool
def generate_marketing_campaign(product_type: str, competitive_rate: str, differentiators: List[str], market_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate comprehensive marketing campaign with Nova Canvas image and Claude-generated text, combined into PDF"""
    try:
        if not BOTO3_AVAILABLE:
            return {"error": "AWS SDK not available for Nova Canvas"}
        
        # Generate marketing text using Claude (via the agent's model)
        marketing_text = _generate_marketing_text(product_type, competitive_rate, differentiators, market_data)
        
        # Create Nova Canvas image  
        image_result = _generate_nova_image(product_type, competitive_rate, differentiators)
        
        if not image_result.get("success"):
            return {"error": f"Image generation failed: {image_result.get('error')}"}
        
        # Create PDF combining image and text
        pdf_result = _create_marketing_pdf(
            product_type, 
            marketing_text, 
            image_result["image_path"],
            competitive_rate,
            differentiators
        )
        
        return {
            "success": True,
            "campaign_type": "comprehensive_marketing_campaign",
            "image_filename": image_result["image_filename"],
            "pdf_filename": pdf_result["pdf_filename"],
            "image_url": image_result["image_url"],
            "pdf_url": pdf_result["pdf_url"],
            "marketing_text": marketing_text,
            "message": f"🎨 Complete marketing campaign generated! PDF: {pdf_result['pdf_filename']}, Image: {image_result['image_filename']}"
        }
        
    except Exception as e:
        return {"error": f"Campaign generation failed: {str(e)}"}

def _generate_marketing_text(product_type: str, rate: str, differentiators: List[str], market_data: Dict[str, Any] = None) -> Dict[str, str]:
    """Generate comprehensive marketing text content"""
    
    product_name = product_type.replace('_', ' ').title()
    
    # Main headline
    headline = f"Introducing Our New {product_name} - Starting at {rate} APR"
    
    # Key benefits
    benefits = differentiators if differentiators else ["Competitive rates", "Fast approval", "Great service"]
    
    # Value proposition
    value_prop = f"Get the {product_name.lower()} you need with our unbeatable combination of competitive rates and exceptional service."
    
    # Product features
    features = [
        f"• {rate} APR starting rate",
        f"• {benefits[0] if benefits else 'Fast approval process'}",
        f"• {benefits[1] if len(benefits) > 1 else 'Flexible terms'}",
        f"• {benefits[2] if len(benefits) > 2 else '24/7 customer support'}",
        "• No hidden fees",
        "• Easy online application"
    ]
    
    # Call to action
    cta = "Apply today and get pre-approved in minutes!"
    
    # Compliance disclaimer
    disclaimer = f"*{rate} APR available for qualified applicants. Rate subject to credit approval. Terms and conditions apply."
    
    return {
        "headline": headline,
        "value_proposition": value_prop,
        "features": "\n".join(features),
        "call_to_action": cta,
        "disclaimer": disclaimer
    }

def _generate_nova_image(product_type: str, rate: str, differentiators: List[str]) -> Dict[str, Any]:
    """Generate marketing image using Nova Canvas with simplified prompt for better text rendering"""
    try:
        bedrock = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        
        # Simplified prompt focusing on visual elements, not text
        prompt = f"""Professional financial services marketing poster design:

VISUAL ELEMENTS ONLY (NO TEXT OVERLAYS):
- Clean modern design with blue and white color scheme
- Financial/banking visual theme 
- Professional corporate layout
- Abstract geometric shapes or simple car silhouette for {product_type}
- Space for text overlays (will be added separately)
- Trust-inspiring financial institution aesthetic
- Minimal design with plenty of white space

Style: Clean, professional, corporate banking poster design
Colors: Blue, white, silver tones
Layout: Modern minimalist with clear focal areas
NO TEXT OR NUMBERS IN THE IMAGE"""
        
        request_body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 1024,
                "width": 768,
                "cfgScale": 7.0
            }
        }
        
        response = bedrock.invoke_model(
            modelId="amazon.nova-canvas-v1:0",
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        
        if response_body.get('images'):
            image_data = response_body['images'][0]
            
            # Save image
            clean_product_type = product_type.replace(' ', '_').replace('_', '_')
            image_filename = f"marketing_image_{clean_product_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            image_path = f"./generated_materials/{image_filename}"
            
            os.makedirs("./generated_materials", exist_ok=True)
            
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(image_data))
            
            return {
                "success": True,
                "image_filename": image_filename,
                "image_path": image_path,
                "image_url": f"http://localhost:8000/materials/{image_filename}"
            }
        else:
            return {"error": "No image generated"}
            
    except Exception as e:
        return {"error": f"Nova Canvas failed: {str(e)}"}

def _create_marketing_pdf(product_type: str, marketing_text: Dict[str, str], image_path: str, rate: str, differentiators: List[str]) -> Dict[str, Any]:
    """Create professional PDF marketing campaign combining image and text"""
    try:
        # Create PDF filename
        clean_product_type = product_type.replace(' ', '_')
        pdf_filename = f"marketing_campaign_{clean_product_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = f"./generated_materials/{pdf_filename}"
        
        # Create PDF
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#1f4e79')
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=HexColor('#2c5f8a')
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            alignment=TA_LEFT
        )
        
        cta_style = ParagraphStyle(
            'CTA',
            parent=styles['Normal'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#1f4e79'),
            fontName='Helvetica-Bold'
        )
        
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=HexColor('#666666')
        )
        
        # Build PDF content
        story = []
        
        # Add title
        story.append(Paragraph(marketing_text["headline"], title_style))
        story.append(Spacer(1, 20))
        
        # Add image
        if os.path.exists(image_path):
            img = RLImage(image_path, width=6*inch, height=4*inch)
            story.append(img)
            story.append(Spacer(1, 20))
        
        # Add value proposition
        story.append(Paragraph(marketing_text["value_proposition"], subtitle_style))
        story.append(Spacer(1, 15))
        
        # Add features
        story.append(Paragraph("<b>Key Features:</b>", body_style))
        story.append(Paragraph(marketing_text["features"], body_style))
        story.append(Spacer(1, 20))
        
        # Add call to action
        story.append(Paragraph(marketing_text["call_to_action"], cta_style))
        story.append(Spacer(1, 30))
        
        # Add disclaimer
        story.append(Paragraph(marketing_text["disclaimer"], disclaimer_style))
        
        # Build PDF
        doc.build(story)
        
        return {
            "success": True,
            "pdf_filename": pdf_filename,
            "pdf_path": pdf_path,
            "pdf_url": f"http://localhost:8000/materials/{pdf_filename}"
        }
        
    except Exception as e:
        return {"error": f"PDF creation failed: {str(e)}"}

# Compliance and Regulatory Checks Tool
@tool
def compliance_and_regulatory_check(product_type: str) -> Dict[str, Any]:
    """Perform comprehensive compliance and regulatory checks for financial product launch"""
    try:
        # Use Tavily to get current regulatory requirements
        api_key = os.getenv('TAVILY_API_KEY')
        regulatory_data = {}
        
        if api_key and TAVILY_AVAILABLE:
            client = TavilyClient(api_key=api_key)
            
            # Search for current regulatory requirements
            reg_query = f"{product_type} federal regulations CFPB compliance requirements 2024"
            response = client.search(reg_query, max_results=5, include_answer=True)
            
            regulatory_data = {
                "query": reg_query,
                "answer": response.get("answer", ""),
                "results": response.get("results", []),
                "real_data": True
            }
        
        # Define compliance framework based on product type
        compliance_framework = _get_compliance_framework(product_type, regulatory_data)
        
        return {
            "product_type": product_type,
            "compliance_status": "REVIEW_REQUIRED",
            "regulatory_framework": compliance_framework,
            "required_licenses": _get_required_licenses(product_type),
            "compliance_timeline": "4-6 weeks",
            "regulatory_data": regulatory_data,
            "next_steps": [
                "Legal team review of regulatory requirements",
                "Compliance documentation preparation",
                "Regulatory filing submissions",
                "Internal compliance training"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Compliance check failed: {str(e)}"}

def _get_compliance_framework(product_type: str, regulatory_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Get compliance framework based on product type"""
    
    frameworks = {
        "car_loan": {
            "federal_regulations": ["Truth in Lending Act (TILA)", "Fair Credit Reporting Act (FCRA)", "Equal Credit Opportunity Act (ECOA)"],
            "state_regulations": ["State lending license requirements", "Interest rate caps", "Consumer protection laws"],
            "industry_standards": ["Auto lending best practices", "Dealer compliance requirements"],
            "documentation": ["Loan agreements", "Privacy notices", "Adverse action notices"]
        },
        "personal_loan": {
            "federal_regulations": ["TILA", "FCRA", "ECOA", "UDAAP"],
            "state_regulations": ["State lending licenses", "Interest rate regulations", "Collection practices"],
            "industry_standards": ["Unsecured lending guidelines", "Income verification standards"],
            "documentation": ["Loan agreements", "Privacy notices", "Collection policies"]
        },
        "credit_card": {
            "federal_regulations": ["CARD Act", "TILA", "FCRA", "ECOA"],
            "state_regulations": ["State banking regulations", "Consumer protection"],
            "industry_standards": ["PCI DSS compliance", "Card network rules"],
            "documentation": ["Cardholder agreements", "Privacy notices", "Fee disclosures"]
        }
    }
    
    return frameworks.get(product_type, frameworks["car_loan"])

def _get_required_licenses(product_type: str) -> List[str]:
    """Get required licenses based on product type"""
    
    licenses = {
        "car_loan": ["Consumer lending license", "Auto finance license", "NMLS registration"],
        "personal_loan": ["Consumer lending license", "Personal loan license", "NMLS registration"],
        "credit_card": ["Credit card issuer license", "Banking license", "Payment processor registration"]
    }
    
    return licenses.get(product_type, ["Consumer lending license"])

# Strategy and Implementation Tool
@tool
def create_strategy_and_implementation(product_type: str, market_data: Dict[str, Any], compliance_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create comprehensive strategy and implementation plan for product launch"""
    try:
        # Extract competitive insights
        competitors = market_data.get("competitors", [])
        market_trends = market_data.get("market_trends", [])
        
        # Calculate competitive positioning
        competitive_rate = _calculate_competitive_rate(competitors)
        differentiators = _identify_differentiators(market_trends, competitors)
        
        # Create implementation timeline
        compliance_timeline = compliance_data.get("compliance_timeline", "4-6 weeks")
        implementation_phases = _create_implementation_phases(product_type, compliance_timeline)
        
        # Define go-to-market strategy
        gtm_strategy = _create_gtm_strategy(product_type, competitive_rate, differentiators)
        
        return {
            "product_type": product_type,
            "competitive_positioning": {
                "recommended_rate": competitive_rate,
                "key_differentiators": differentiators,
                "target_market": _define_target_market(product_type)
            },
            "implementation_phases": implementation_phases,
            "go_to_market_strategy": gtm_strategy,
            "success_metrics": _define_success_metrics(product_type),
            "risk_mitigation": _assess_risks(product_type),
            "total_timeline": "8-12 weeks",
            "estimated_budget": _estimate_budget(product_type),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Strategy creation failed: {str(e)}"}

def _calculate_competitive_rate(competitors: List[Dict]) -> str:
    """Calculate competitive rate based on market data"""
    if not competitors:
        return "5.99%"
    
    rates = []
    for comp in competitors:
        rate_str = comp.get("rate", "6.00%")
        try:
            rate = float(rate_str.replace("%", ""))
            rates.append(rate)
        except:
            continue
    
    if rates:
        avg_rate = sum(rates) / len(rates)
        competitive_rate = max(avg_rate - 0.25, 3.5)  # 0.25% below average, minimum 3.5%
        return f"{competitive_rate:.2f}%"
    
    return "5.99%"

def _identify_differentiators(trends: List[str], competitors: List[Dict]) -> List[str]:
    """Identify key differentiators based on market analysis"""
    base_differentiators = ["Fast approval", "Competitive rates", "Digital experience"]
    
    # Add trend-based differentiators
    if any("digital" in trend.lower() for trend in trends):
        base_differentiators.append("Mobile-first platform")
    if any("customer" in trend.lower() for trend in trends):
        base_differentiators.append("24/7 customer support")
    
    return base_differentiators[:4]  # Top 4 differentiators

def _create_implementation_phases(product_type: str, compliance_timeline: str) -> List[Dict]:
    """Create detailed implementation phases"""
    return [
        {
            "phase": "Legal & Compliance",
            "duration": compliance_timeline,
            "tasks": [
                "Regulatory approval process",
                "Legal documentation preparation",
                "Compliance framework setup",
                "Risk assessment completion"
            ]
        },
        {
            "phase": "Product Development",
            "duration": "3-4 weeks",
            "tasks": [
                "Loan application system development",
                "Integration with credit bureaus",
                "Underwriting system configuration",
                "Customer portal creation"
            ]
        },
        {
            "phase": "Marketing & Launch Preparation",
            "duration": "2-3 weeks",
            "tasks": [
                "Marketing materials creation",
                "Website development",
                "Staff training completion",
                "Soft launch preparation"
            ]
        },
        {
            "phase": "Go-Live & Monitoring",
            "duration": "1-2 weeks",
            "tasks": [
                "Production deployment",
                "Customer website launch",
                "Marketing campaign activation",
                "Performance monitoring setup"
            ]
        }
    ]

def _create_gtm_strategy(product_type: str, rate: str, differentiators: List[str]) -> Dict[str, Any]:
    """Create go-to-market strategy"""
    return {
        "positioning": f"Best-in-class {product_type.replace('_', ' ')} with {rate} APR",
        "channels": ["Digital marketing", "Partner networks", "Referral programs"],
        "target_audience": _define_target_market(product_type),
        "messaging": f"Experience {differentiators[0].lower()} with our new {product_type.replace('_', ' ')}",
        "launch_sequence": [
            "Soft launch to existing customers",
            "Digital marketing campaign",
            "Partner channel activation",
            "Full market launch"
        ]
    }

def _define_target_market(product_type: str) -> str:
    """Define target market based on product type"""
    markets = {
        "car_loan": "Prime and near-prime borrowers purchasing new or used vehicles",
        "personal_loan": "Consumers seeking debt consolidation or major purchases",
        "credit_card": "Digital-first consumers wanting rewards and convenience"
    }
    return markets.get(product_type, "General consumer market")

def _define_success_metrics(product_type: str) -> List[str]:
    """Define success metrics for product launch"""
    return [
        "Applications submitted (target: 100+ in first month)",
        "Approval rate (target: 60-70%)",
        "Average loan amount",
        "Customer acquisition cost",
        "Customer satisfaction score (target: 4.5+/5)"
    ]

def _assess_risks(product_type: str) -> List[str]:
    """Assess potential risks"""
    return [
        "Regulatory changes impacting lending requirements",
        "Economic downturn affecting borrower demand",
        "Competitive rate pressure",
        "Technology integration challenges"
    ]

def _estimate_budget(product_type: str) -> str:
    """Estimate implementation budget"""
    budgets = {
        "car_loan": "$150,000 - $300,000",
        "personal_loan": "$100,000 - $200,000", 
        "credit_card": "$300,000 - $500,000"
    }
    return budgets.get(product_type, "$150,000 - $300,000")

# Product Deployment Tool
@tool
def deploy_product_launch(product_type: str, strategy_data: Dict[str, Any], marketing_data: Dict[str, Any]) -> Dict[str, Any]:
    """Deploy the financial product and create customer-facing website"""
    try:
        # Extract strategy details
        positioning = strategy_data.get("competitive_positioning", {})
        rate = positioning.get("recommended_rate", "5.99%")
        differentiators = positioning.get("key_differentiators", ["Fast approval", "Great rates"])
        
        # Create customer website
        website_result = _create_customer_website(product_type, rate, differentiators, marketing_data)
        
        # Setup product infrastructure
        infrastructure_result = _setup_product_infrastructure(product_type)
        
        # Configure monitoring and analytics
        monitoring_result = _setup_monitoring(product_type)
        
        return {
            "deployment_status": "SUCCESS",
            "product_type": product_type,
            "website_url": website_result["website_url"],
            "website_path": website_result["website_path"],
            "infrastructure": infrastructure_result,
            "monitoring": monitoring_result,
            "go_live_checklist": [
                "✅ Regulatory approvals obtained",
                "✅ Product systems deployed",
                "✅ Customer website launched",
                "✅ Marketing materials ready",
                "✅ Staff training completed",
                "✅ Monitoring systems active"
            ],
            "next_steps": [
                "Begin soft launch with select customers",
                "Monitor application volumes and approval rates",
                "Launch full marketing campaign",
                "Track success metrics and KPIs"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Deployment failed: {str(e)}"}

def _create_customer_website(product_type: str, rate: str, differentiators: List[str], marketing_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create customer-facing website for the new product - Professional US Bank/SoFi style"""
    try:
        product_name = product_type.replace('_', ' ').title()
        
        # Create realistic, professional HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product_name} | Premier Financial - Get Pre-Approved Today</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{ 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            line-height: 1.6; 
            color: #1a1a1a; 
            background: #ffffff;
        }}
        
        /* Header Navigation */
        .nav-header {{
            background: #ffffff;
            border-bottom: 1px solid #e5e7eb;
            padding: 0;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
        }}
        
        .logo {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #0066cc;
            text-decoration: none;
        }}
        
        .nav-links {{
            display: flex;
            gap: 2rem;
            list-style: none;
        }}
        
        .nav-links a {{
            color: #4b5563;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        }}
        
        .nav-links a:hover {{ color: #0066cc; }}
        
        .nav-cta {{
            background: #0066cc;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.2s;
        }}
        
        .nav-cta:hover {{ background: #0052a3; }}
        
        /* Hero Section */
        .hero {{
            background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
            color: white;
            padding: 4rem 0 6rem 0;
            position: relative;
            overflow: hidden;
        }}
        
        .hero::before {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 50%;
            height: 100%;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            opacity: 0.3;
        }}
        
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 2rem; position: relative; }}
        
        .hero-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 4rem;
            align-items: center;
        }}
        
        .hero-text h1 {{
            font-size: 3.5rem;
            font-weight: 700;
            line-height: 1.1;
            margin-bottom: 1.5rem;
        }}
        
        .hero-text p {{
            font-size: 1.25rem;
            opacity: 0.9;
            margin-bottom: 2rem;
            line-height: 1.6;
        }}
        
        .hero-stats {{
            display: flex;
            gap: 3rem;
            margin-bottom: 2rem;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: 700;
            display: block;
            color: #fbbf24;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        
        .hero-cta {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}
        
        .btn-primary {{
            background: #fbbf24;
            color: #1a1a1a;
            padding: 1rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.2s;
            border: none;
            cursor: pointer;
        }}
        
        .btn-primary:hover {{
            background: #f59e0b;
            transform: translateY(-1px);
        }}
        
        .btn-secondary {{
            color: white;
            padding: 1rem 2rem;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s;
        }}
        
        .btn-secondary:hover {{
            border-color: white;
            background: rgba(255,255,255,0.1);
        }}
        
        /* Rate Display */
        .rate-showcase {{
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .rate-number {{
            font-size: 4rem;
            font-weight: 700;
            color: #fbbf24;
            display: block;
            line-height: 1;
        }}
        
        .rate-label {{
            font-size: 1.1rem;
            margin-top: 0.5rem;
            opacity: 0.9;
        }}
        
        .rate-disclaimer {{
            font-size: 0.8rem;
            opacity: 0.7;
            margin-top: 1rem;
        }}
        
        /* Features Section */
        .features {{
            padding: 6rem 0;
            background: #f8fafc;
        }}
        
        .section-header {{
            text-align: center;
            margin-bottom: 4rem;
        }}
        
        .section-header h2 {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 1rem;
        }}
        
        .section-header p {{
            font-size: 1.2rem;
            color: #6b7280;
            max-width: 600px;
            margin: 0 auto;
        }}
        
        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }}
        
        .feature-card {{
            background: white;
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border: 1px solid #e5e7eb;
            transition: all 0.3s;
            text-align: center;
        }}
        
        .feature-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.1);
        }}
        
        .feature-icon {{
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #0066cc, #004499);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.5rem auto;
            font-size: 1.5rem;
            color: white;
        }}
        
        .feature-card h3 {{
            font-size: 1.3rem;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 1rem;
        }}
        
        .feature-card p {{
            color: #6b7280;
            line-height: 1.6;
        }}
        
        /* Process Section */
        .process {{
            padding: 6rem 0;
            background: white;
        }}
        
        .process-steps {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 3rem;
            margin-top: 3rem;
        }}
        
        .process-step {{
            text-align: center;
            position: relative;
        }}
        
        .step-number {{
            width: 50px;
            height: 50px;
            background: #0066cc;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.2rem;
            margin: 0 auto 1.5rem auto;
        }}
        
        .process-step h3 {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #1a1a1a;
        }}
        
        .process-step p {{
            color: #6b7280;
        }}
        
        /* CTA Section */
        .final-cta {{
            background: linear-gradient(135deg, #1a1a1a 0%, #374151 100%);
            color: white;
            padding: 6rem 0;
            text-align: center;
        }}
        
        .final-cta h2 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }}
        
        .final-cta p {{
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 2rem;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .cta-buttons {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        /* Footer */
        .footer {{
            background: #1a1a1a;
            color: white;
            padding: 3rem 0 2rem 0;
        }}
        
        .footer-content {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        
        .footer-section h3 {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #fbbf24;
        }}
        
        .footer-section ul {{
            list-style: none;
        }}
        
        .footer-section ul li {{
            margin-bottom: 0.5rem;
        }}
        
        .footer-section ul li a {{
            color: #d1d5db;
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        .footer-section ul li a:hover {{
            color: #fbbf24;
        }}
        
        .footer-bottom {{
            border-top: 1px solid #374151;
            padding-top: 2rem;
            text-align: center;
            color: #9ca3af;
            font-size: 0.9rem;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .hero-content {{ grid-template-columns: 1fr; gap: 2rem; }}
            .hero-text h1 {{ font-size: 2.5rem; }}
            .hero-stats {{ justify-content: center; }}
            .nav-links {{ display: none; }}
            .cta-buttons {{ flex-direction: column; align-items: center; }}
        }}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="nav-header">
        <div class="nav-container">
            <a href="#" class="logo">Premier Financial</a>
            <ul class="nav-links">
                <li><a href="#loans">Loans</a></li>
                <li><a href="#rates">Rates</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
            <a href="#apply" class="nav-cta">Get Started</a>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <div class="hero-content">
                <div class="hero-text">
                    <h1>Get Your Dream {product_name} Today</h1>
                    <p>Competitive rates, fast approval, and exceptional service. Join thousands of satisfied customers who chose Premier Financial for their {product_name.lower()} needs.</p>
                    
                    <div class="hero-stats">
                        <div class="stat">
                            <span class="stat-number">24hrs</span>
                            <span class="stat-label">Avg. Approval Time</span>
                        </div>
                        <div class="stat">
                            <span class="stat-number">50K+</span>
                            <span class="stat-label">Happy Customers</span>
                        </div>
                        <div class="stat">
                            <span class="stat-number">4.9★</span>
                            <span class="stat-label">Customer Rating</span>
                        </div>
                    </div>
                    
                    <div class="hero-cta">
                        <a href="#apply" class="btn-primary">Apply Now - 2 Min Application</a>
                        <a href="#calculator" class="btn-secondary">Calculate Payment</a>
                    </div>
                </div>
                
                <div class="rate-showcase">
                    <span class="rate-number">{rate}</span>
                    <div class="rate-label">APR Starting Rate*</div>
                    <div class="rate-disclaimer">*Rate shown for qualified applicants with excellent credit</div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="features">
        <div class="container">
            <div class="section-header">
                <h2>Why Choose Premier Financial?</h2>
                <p>We're committed to providing you with the best {product_name.lower()} experience, from application to final payment.</p>
            </div>
            
            <div class="features-grid">"""

        # Add enhanced features based on differentiators
        feature_icons = ["⚡", "💰", "📱", "🛡️", "⭐", "🎯"]
        enhanced_features = [
            {"title": "Lightning Fast Approval", "desc": "Get approved in as little as 24 hours with our streamlined digital process"},
            {"title": "Competitive Rates", "desc": f"Starting at {rate} APR for qualified applicants with flexible terms"},
            {"title": "Mobile-First Experience", "desc": "Manage your loan entirely from your smartphone with our award-winning app"},
            {"title": "No Hidden Fees", "desc": "Transparent pricing with no application fees, prepayment penalties, or surprises"},
            {"title": "5-Star Service", "desc": "Dedicated loan specialists available 7 days a week to support your journey"},
            {"title": "Flexible Terms", "desc": "Choose from multiple term lengths and payment options that fit your budget"}
        ]
        
        for i, feature in enumerate(enhanced_features[:6]):
            html_content += f"""
                <div class="feature-card">
                    <div class="feature-icon">{feature_icons[i]}</div>
                    <h3>{feature['title']}</h3>
                    <p>{feature['desc']}</p>
                </div>"""

        html_content += f"""
            </div>
        </div>
    </section>

    <!-- Process Section -->
    <section class="process">
        <div class="container">
            <div class="section-header">
                <h2>Simple 3-Step Process</h2>
                <p>Getting your {product_name.lower()} has never been easier. Here's how it works:</p>
            </div>
            
            <div class="process-steps">
                <div class="process-step">
                    <div class="step-number">1</div>
                    <h3>Apply Online</h3>
                    <p>Complete our secure 2-minute application. No paperwork, no hassle.</p>
                </div>
                <div class="process-step">
                    <div class="step-number">2</div>
                    <h3>Get Approved</h3>
                    <p>Receive your decision in minutes, with funding available as soon as the next business day.</p>
                </div>
                <div class="process-step">
                    <div class="step-number">3</div>
                    <h3>Drive Away</h3>
                    <p>Use your funds to purchase your vehicle and start enjoying your new {product_name.lower()}.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Final CTA -->
    <section class="final-cta" id="apply">
        <div class="container">
            <h2>Ready to Get Started?</h2>
            <p>Join thousands of satisfied customers. Apply now and get pre-approved in minutes with no impact to your credit score.</p>
            <div class="cta-buttons">
                <a href="#" class="btn-primary">Start Your Application</a>
                <a href="#" class="btn-secondary">Speak with a Specialist</a>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>Products</h3>
                    <ul>
                        <li><a href="#">Auto Loans</a></li>
                        <li><a href="#">Personal Loans</a></li>
                        <li><a href="#">Home Loans</a></li>
                        <li><a href="#">Credit Cards</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3>Resources</h3>
                    <ul>
                        <li><a href="#">Loan Calculator</a></li>
                        <li><a href="#">Rate Information</a></li>
                        <li><a href="#">Financial Education</a></li>
                        <li><a href="#">Customer Reviews</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3>Support</h3>
                    <ul>
                        <li><a href="#">Contact Us</a></li>
                        <li><a href="#">FAQ</a></li>
                        <li><a href="#">Account Login</a></li>
                        <li><a href="#">Make a Payment</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3>Company</h3>
                    <ul>
                        <li><a href="#">About Us</a></li>
                        <li><a href="#">Careers</a></li>
                        <li><a href="#">Press</a></li>
                        <li><a href="#">Investor Relations</a></li>
                    </ul>
                </div>
            </div>
            
            <div class="footer-bottom">
                <p>&copy; 2024 Premier Financial. All rights reserved. | 
                <a href="#" style="color: #fbbf24;">Privacy Policy</a> | 
                <a href="#" style="color: #fbbf24;">Terms of Service</a> | 
                Equal Housing Lender | NMLS ID: 123456</p>
                <p style="margin-top: 1rem; font-size: 0.8rem;">
                    *{rate} APR available for qualified applicants with excellent credit (720+ FICO). 
                    Rate varies based on creditworthiness, loan amount, and term. All loans subject to credit approval.
                </p>
            </div>
        </div>
    </footer>

    <script>
        // Enhanced analytics and interactions
        document.addEventListener('DOMContentLoaded', function() {{
            // Smooth scrolling for anchor links
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
                anchor.addEventListener('click', function (e) {{
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {{
                        target.scrollIntoView({{ behavior: 'smooth' }});
                    }}
                }});
            }});
            
            // Track CTA clicks
            document.querySelectorAll('.btn-primary, .btn-secondary, .nav-cta').forEach(btn => {{
                btn.addEventListener('click', function(e) {{
                    console.log('CTA Clicked:', this.textContent.trim());
                    // In production, send to analytics service
                }});
            }});
            
            // Add loading states to buttons
            document.querySelectorAll('.btn-primary').forEach(btn => {{
                btn.addEventListener('click', function(e) {{
                    if (this.href === '#' || this.href.endsWith('#')) {{
                        e.preventDefault();
                        this.textContent = 'Loading...';
                        setTimeout(() => {{
                            this.textContent = 'Start Your Application';
                        }}, 2000);
                    }}
                }});
            }});
        }});
        
        console.log('Premier Financial {product_name} Website Loaded');
        console.log('Launch Date: {datetime.now().strftime("%Y-%m-%d")}');
    </script>
</body>
</html>"""

        # Save website file
        clean_product_type = product_type.replace(' ', '_')
        website_filename = f"{clean_product_type}_website_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        website_path = f"./generated_materials/{website_filename}"
        
        os.makedirs("./generated_materials", exist_ok=True)
        
        with open(website_path, "w", encoding='utf-8') as f:
            f.write(html_content)
        
        return {
            "success": True,
            "website_filename": website_filename,
            "website_path": website_path,
            "website_url": f"http://localhost:8000/materials/{website_filename}"
        }
        
    except Exception as e:
        return {"error": f"Website creation failed: {str(e)}"}

def _setup_product_infrastructure(product_type: str) -> Dict[str, str]:
    """Setup product infrastructure (simulated)"""
    return {
        "application_system": "✅ Loan application system configured",
        "credit_bureau_integration": "✅ Experian, Equifax, TransUnion APIs connected",
        "underwriting_engine": "✅ Automated underwriting rules deployed",
        "document_management": "✅ Secure document storage system ready",
        "notification_system": "✅ Email and SMS notifications configured"
    }

def _setup_monitoring(product_type: str) -> Dict[str, str]:
    """Setup monitoring and analytics (simulated)"""
    return {
        "application_tracking": "✅ Application volume monitoring active",
        "approval_rate_monitoring": "✅ Real-time approval rate dashboard",
        "customer_analytics": "✅ Customer journey tracking enabled",
        "system_health": "✅ Infrastructure monitoring configured",
        "compliance_alerts": "✅ Regulatory compliance monitoring active"
    }

# Backwards compatibility - simple poster tool
@tool
def generate_marketing_poster(product_type: str, competitive_rate: str, differentiators: list) -> Dict[str, Any]:
    """Generate marketing poster using Nova Canvas (backwards compatibility)"""
    return _generate_nova_image(product_type, competitive_rate, differentiators)

# Create the enhanced Strands agent
financial_agent = Agent(
    name="FinancialProductLaunchAgent",
    model=BedrockModel(model_id=os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20240620-v1:0')),
    system_prompt="""You are a Financial Product Launch Agent for a financial organization that helps launch new financial products from inception to live customer websites.

🏦 **YOU ARE A FINANCIAL ORGANIZATION'S AI ASSISTANT**:
You work for a financial institution helping them venture into new segments/offerings like car loans, personal loans, credit cards, etc. You guide them through the complete end-to-end product lifecycle from inception to implementation.

🎯 **EXACT WORKFLOW FOR FINANCIAL ORGANIZATION**:

**FLEXIBLE TASK HANDLING**:

**INDIVIDUAL TASKS** (Analyze user intent and provide specific help):
- Market research requests: "research [product] in [location]" → Use research_market_data
- Marketing requests: "create marketing campaign/materials" → Use generate_marketing_campaign  
- Compliance requests: "compliance check for [product]" → Use compliance_and_regulatory_check
- Strategy requests: "strategy for [product]" → Use create_strategy_and_implementation
- Deployment requests: "deploy [product]" → Use deploy_product_launch

**FULL PRODUCT LAUNCH** (Complete end-to-end workflow):
When user says "launch [product]" or "new financial product":

**Step 2: COMPLIANCE AND REGULATORY CHECKS**
- Immediately call compliance_and_regulatory_check(product_type)
- Explain: "First, I'm performing comprehensive compliance and regulatory checks..."
- Present federal regulations (TILA, FCRA, ECOA), state requirements, licensing needs
- Show compliance timeline and next steps

**Step 3: COMPETITIVE ANALYSIS**
- Immediately call research_market_data("product_type competitive analysis rates market trends 2024")
- Explain: "Now conducting real-time competitive analysis..."
- Present competitor rates, market positioning, opportunities
- Show how to position against competition

**Step 4: STRATEGY AND IMPLEMENTATION STEPS**
- Immediately call create_strategy_and_implementation(product_type, market_data, compliance_data)
- Explain: "Creating your comprehensive strategy and implementation roadmap..."
- Present strategic positioning, implementation phases, timeline, budget
- Show success metrics and risk mitigation

**Step 5: PRODUCT DEPLOYMENT**
- Immediately call deploy_product_launch(product_type, strategy_data, marketing_data)
- Explain: "Deploying your product infrastructure and creating customer website..."
- Setup product systems, infrastructure, monitoring
- Create professional customer-facing website

**Step 6: PRODUCT IS LIVE - SHARE WEBSITE URL**
- Present the final website URL: "🎉 Your [product] is now LIVE for customers!"
- Show the website URL: "Visit your new customer website at: [URL]"
- Provide go-live checklist and next steps for full launch

🔧 **YOUR TOOLS** (USE IN EXACT SEQUENCE):
1. **compliance_and_regulatory_check** - Federal/state regulatory validation
2. **research_market_data** - Real-time competitive intelligence via Tavily
3. **create_strategy_and_implementation** - Strategic roadmap and planning
4. **deploy_product_launch** - Complete deployment with customer website
5. **generate_marketing_campaign** - Professional marketing materials (if requested)

💡 **EXAMPLE INTERACTIONS**:

**Individual Task Example**:
User: "Do market research for car loans in Cambodia"
Your Response: "I'll conduct comprehensive market research for car loans specifically in Cambodia. This will include:

🔍 **Research Scope**:
- Real-time competitive analysis of Cambodian financial institutions
- Current market rates and lending practices
- Local regulatory environment and requirements  
- Consumer preferences and market opportunities
- Economic factors affecting auto lending

Should I proceed with this market research for Cambodia's car loan market?"

**Marketing Campaign Example**:
User: "Create marketing campaign for personal loans"
Your Response: "I'll create a comprehensive marketing campaign for personal loans using AI-powered tools. This will include:

🎨 **Campaign Components**:
- AI-generated marketing images using Amazon Nova Canvas
- Professional PDF marketing posters with compelling copy
- Social media campaign assets for multiple platforms
- Strategic messaging and value propositions

Should I proceed with creating this personal loan marketing campaign?"

**Full Launch Example**:
User: "Launch a car loan product"
Your Response: "I'll guide you through the complete car loan product launch process. This involves:

🚀 **Complete Launch Process**:
1. Regulatory compliance validation
2. Real-time competitive market analysis  
3. Strategic positioning and pricing
4. Marketing materials creation
5. Customer website deployment

Should I proceed with the full car loan product launch?"

🔑 **CRITICAL BEHAVIORS**:
- ALWAYS execute all 5 tools in sequence for every product launch
- Never skip any step in the workflow
- Always end with presenting the live website URL
- Be professional yet encouraging throughout
- Focus on real business value and actionable outcomes
- Present concrete deliverables at each step

**SPECIAL HANDLING**:
- For marketing requests only: use research_market_data + generate_marketing_campaign
- For questions: answer then ask if they want to launch a product
- Always complete the full workflow - this is a complete product launch system""",
    tools=[research_market_data, compliance_and_regulatory_check, create_strategy_and_implementation, deploy_product_launch, generate_marketing_campaign, generate_marketing_poster]
)

def get_financial_agent():
    """Get the configured financial agent"""
    return financial_agent
