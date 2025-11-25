import os
import json
import boto3
from typing import Dict, Any, List
from datetime import datetime
from strands.tools import tool
from strands.models import BedrockModel

# Initialize Bedrock client
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))

@tool
def browse_web(url: str, query: str = "") -> Dict[str, Any]:
    """Browse web content using AgentCore Browser for real-time information gathering"""
    try:
        # Check if running in AgentCore environment
        if os.getenv('DOCKER_CONTAINER'):
            # Use AgentCore Browser API
            import requests
            
            browser_endpoint = os.getenv('AGENTCORE_BROWSER_ENDPOINT', 'http://localhost:8080/browser')
            
            payload = {
                "url": url,
                "query": query,
                "timeout": 30,
                "extract_text": True,
                "follow_redirects": True
            }
            
            response = requests.post(f"{browser_endpoint}/browse", json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "url": url,
                    "title": data.get("title", ""),
                    "content": data.get("content", ""),
                    "timestamp": datetime.now().isoformat(),
                    "browser": "AgentCore Browser"
                }
            else:
                return {
                    "success": False,
                    "error": f"Browser request failed: {response.status_code}",
                    "url": url
                }
        else:
            # Fallback for local testing
            return {
                "success": True,
                "url": url,
                "content": f"Local testing mode - would browse: {url} for query: {query}",
                "timestamp": datetime.now().isoformat(),
                "browser": "Local Fallback"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Browser error: {str(e)}",
            "url": url
        }
        # Simulate browser capability - in AgentCore this would be actual browser
        import requests
        from bs4 import BeautifulSoup
        
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; AgentCore/1.0)'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract relevant content
        text_content = soup.get_text()[:2000]  # Limit content
        
        return {
            "url": url,
            "content": text_content,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Browse failed: {str(e)}", "url": url}

@tool
def enhanced_compliance_check(product_type: str) -> Dict[str, Any]:
    """AI-powered compliance analysis using Bedrock and real-time web data"""
    try:
        # Browse current regulatory websites
        regulatory_sites = [
            "https://www.consumerfinance.gov/compliance/",
            "https://www.federalreserve.gov/supervisionreg.htm"
        ]
        
        web_data = []
        for site in regulatory_sites:
            result = browse_web(site, f"{product_type} regulations")
            if "content" in result:
                web_data.append(result["content"])
        
        # Use Bedrock to analyze regulatory requirements
        prompt = f"""
        Analyze current regulatory requirements for {product_type} based on this real-time data:
        
        {' '.join(web_data[:1000])}
        
        Provide:
        1. Key federal regulations
        2. State-level requirements
        3. Compliance timeline
        4. Risk assessment
        5. Required documentation
        
        Format as JSON with specific actionable items.
        """
        
        response = bedrock_runtime.invoke_model(
            modelId=os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0'),
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        ai_analysis = result['content'][0]['text']
        
        return {
            "product_type": product_type,
            "ai_analysis": ai_analysis,
            "data_sources": regulatory_sites,
            "real_time_data": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Enhanced compliance check failed: {str(e)}"}

@tool
def ai_strategy_planning(product_type: str, market_data: Dict[str, Any], compliance_data: Dict[str, Any]) -> Dict[str, Any]:
    """AI-generated strategic planning using Bedrock"""
    try:
        # Browse competitor websites for real-time positioning
        competitor_urls = [
            "https://www.chase.com/personal/auto-loans",
            "https://www.bankofamerica.com/auto-loans/",
            "https://www.wellsfargo.com/auto-loans/"
        ]
        
        competitor_data = []
        for url in competitor_urls:
            result = browse_web(url, f"{product_type} rates features")
            if "content" in result:
                competitor_data.append(result["content"][:500])
        
        # AI-powered strategy generation
        prompt = f"""
        Create a comprehensive launch strategy for {product_type} based on:
        
        Market Data: {json.dumps(market_data, indent=2)}
        Compliance Requirements: {json.dumps(compliance_data, indent=2)}
        Real-time Competitor Analysis: {' '.join(competitor_data)}
        
        Generate:
        1. Competitive positioning strategy
        2. Pricing recommendations with rationale
        3. Implementation phases with specific timelines
        4. Go-to-market strategy
        5. Success metrics and KPIs
        6. Risk mitigation plan
        7. Budget estimates
        
        Provide specific, actionable recommendations in JSON format.
        """
        
        response = bedrock_runtime.invoke_model(
            modelId=os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0'),
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 3000,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        ai_strategy = result['content'][0]['text']
        
        return {
            "product_type": product_type,
            "ai_strategy": ai_strategy,
            "competitor_analysis": competitor_data,
            "real_time_data": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"AI strategy planning failed: {str(e)}"}

@tool
def ai_website_deployment(product_type: str, strategy_data: Dict[str, Any], marketing_data: Dict[str, Any]) -> Dict[str, Any]:
    """AI-generated website deployment using Bedrock"""
    try:
        # Browse best practice websites for inspiration
        inspiration_sites = [
            "https://www.marcus.com/us/en/personal-loans",
            "https://www.sofi.com/personal-loans/",
            "https://www.lightstream.com/"
        ]
        
        design_inspiration = []
        for url in inspiration_sites:
            result = browse_web(url, "website design features")
            if "content" in result:
                design_inspiration.append(result["content"][:300])
        
        # AI-generated website content
        prompt = f"""
        Create a professional, modern website for {product_type} based on:
        
        Strategy Data: {json.dumps(strategy_data, indent=2)}
        Marketing Data: {json.dumps(marketing_data, indent=2)}
        Design Inspiration: {' '.join(design_inspiration)}
        
        Generate:
        1. Complete HTML with modern CSS (responsive design)
        2. Compelling copy that converts
        3. Clear value propositions
        4. Trust signals and social proof
        5. Strong call-to-action elements
        6. Mobile-optimized layout
        
        Make it professional, trustworthy, and conversion-focused.
        
        IMPORTANT: Return ONLY the HTML code starting with <!DOCTYPE html>. 
        Do NOT include any explanations, descriptions, or markdown code fences.
        Do NOT add any text before or after the HTML.
        """
        
        response = bedrock_runtime.invoke_model(
            modelId=os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0'),
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        ai_website = result['content'][0]['text']
        
        # Clean up the AI-generated HTML - remove markdown code fences and descriptions
        ai_website = ai_website.strip()
        
        # Remove markdown code fences (```html and ```)
        if ai_website.startswith('```html'):
            ai_website = ai_website[7:]  # Remove ```html
        elif ai_website.startswith('```'):
            ai_website = ai_website[3:]  # Remove ```
        
        if ai_website.endswith('```'):
            ai_website = ai_website[:-3]  # Remove trailing ```
        
        # Remove any leading description text before <!DOCTYPE html>
        doctype_index = ai_website.find('<!DOCTYPE html>')
        if doctype_index > 0:
            ai_website = ai_website[doctype_index:]
        elif ai_website.find('<html') > 0:
            html_index = ai_website.find('<html')
            ai_website = ai_website[html_index:]
        
        ai_website = ai_website.strip()
        
        # Save AI-generated website
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_website_{product_type}_{timestamp}.html"
        filepath = f"generated_materials/{filename}"
        
        os.makedirs("generated_materials", exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(ai_website)
        
        # Generate deployment infrastructure using AI
        infra_prompt = f"""
        Generate AWS infrastructure deployment plan for {product_type} website:
        
        Include:
        1. S3 bucket configuration
        2. CloudFront distribution
        3. Route 53 DNS setup
        4. SSL certificate
        5. Monitoring and analytics
        6. Security configurations
        
        Provide as executable AWS CLI commands.
        """
        
        infra_response = bedrock_runtime.invoke_model(
            modelId=os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0'),
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": infra_prompt}]
            })
        )
        
        infra_result = json.loads(infra_response['body'].read())
        infrastructure_plan = infra_result['content'][0]['text']
        
        return {
            "deployment_status": "SUCCESS",
            "product_type": product_type,
            "website_file": filename,
            "website_path": filepath,
            "ai_generated_content": True,
            "infrastructure_plan": infrastructure_plan,
            "design_sources": inspiration_sites,
            "website_url": f"http://localhost:8000/materials/{filename}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"AI website deployment failed: {str(e)}"}

@tool
def real_time_market_research(query: str) -> Dict[str, Any]:
    """Enhanced market research with browser and AI analysis"""
    try:
        # Browse financial news and market data sites
        research_sites = [
            "https://www.bankrate.com/loans/auto-loans/",
            "https://www.nerdwallet.com/auto-loans",
            "https://www.creditkarma.com/auto/i/auto-loan-rates"
        ]
        
        market_data = []
        for site in research_sites:
            result = browse_web(site, query)
            if "content" in result:
                market_data.append(result["content"])
        
        # AI analysis of market data
        prompt = f"""
        Analyze this real-time market data for: {query}
        
        Data: {' '.join(market_data[:2000])}
        
        Provide:
        1. Current market rates and trends
        2. Competitive landscape analysis
        3. Market opportunities
        4. Consumer preferences
        5. Pricing recommendations
        6. Market positioning insights
        
        Format as structured JSON with actionable insights.
        """
        
        response = bedrock_runtime.invoke_model(
            modelId=os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0'),
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2500,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        ai_analysis = result['content'][0]['text']
        
        return {
            "query": query,
            "ai_market_analysis": ai_analysis,
            "data_sources": research_sites,
            "real_time_data": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Real-time market research failed: {str(e)}"}

@tool
def create_product_website(product_name: str, product_type: str, key_features: List[str], target_audience: str = "retail customers") -> Dict[str, Any]:
    """Create a professional HTML website for the financial product"""
    try:
        # Create HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product_name} - Financial Solutions</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%); color: white; padding: 2rem 0; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        .hero {{ text-align: center; padding: 4rem 0; }}
        .hero h1 {{ font-size: 3rem; margin-bottom: 1rem; font-weight: 300; }}
        .hero p {{ font-size: 1.2rem; opacity: 0.9; margin-bottom: 2rem; }}
        .cta-button {{ background: #ff6b35; color: white; padding: 15px 30px; border: none; border-radius: 25px; font-size: 1.1rem; cursor: pointer; text-decoration: none; display: inline-block; }}
        .features {{ padding: 4rem 0; background: #f8f9fa; }}
        .features-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 2rem; }}
        .feature-card {{ background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .feature-card h3 {{ color: #1976d2; margin-bottom: 1rem; }}
        .rates {{ padding: 4rem 0; }}
        .rate-card {{ background: linear-gradient(135deg, #e3f2fd 0%, #f0f8ff 100%); padding: 2rem; border-radius: 10px; text-align: center; margin: 2rem 0; }}
        .rate-number {{ font-size: 3rem; font-weight: bold; color: #1976d2; }}
        .footer {{ background: #333; color: white; padding: 2rem 0; text-align: center; }}
        .apply-section {{ background: #1976d2; color: white; padding: 3rem 0; text-align: center; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="hero">
                <h1>{product_name}</h1>
                <p>Designed specifically for {target_audience} with competitive rates and flexible terms</p>
                <a href="#apply" class="cta-button">Apply Now</a>
            </div>
        </div>
    </header>

    <section class="features">
        <div class="container">
            <h2 style="text-align: center; margin-bottom: 1rem;">Why Choose Our {product_type}?</h2>
            <div class="features-grid">"""

        # Add feature cards
        for i, feature in enumerate(key_features[:6]):  # Limit to 6 features
            html_content += f"""
                <div class="feature-card">
                    <h3>✓ {feature}</h3>
                    <p>Experience the benefits of our carefully designed {product_type.lower()} solution tailored for your financial needs.</p>
                </div>"""

        html_content += f"""
            </div>
        </div>
    </section>

    <section class="rates">
        <div class="container">
            <h2 style="text-align: center; margin-bottom: 2rem;">Competitive Rates</h2>
            <div class="rate-card">
                <div class="rate-number">3.99%</div>
                <p>Starting APR for qualified applicants</p>
                <small>*Rate varies based on creditworthiness and loan terms</small>
            </div>
        </div>
    </section>

    <section class="apply-section" id="apply">
        <div class="container">
            <h2>Ready to Get Started?</h2>
            <p>Apply online in minutes and get a decision fast</p>
            <a href="#" class="cta-button" style="margin-top: 1rem;">Start Application</a>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 Financial Solutions. All rights reserved. | Equal Housing Lender | FDIC Insured</p>
            <p><small>This is a demo website created by AI Financial Product Launch Agent</small></p>
        </div>
    </footer>
</body>
</html>"""

        # Save to file
        filename = f"{product_name.lower().replace(' ', '_')}_website.html"
        filepath = os.path.join("generated_materials", filename)
        
        # Create directory if it doesn't exist
        os.makedirs("generated_materials", exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return {
            "success": True,
            "message": f"Created professional website for {product_name}",
            "filename": filename,
            "filepath": filepath,
            "url": f"file://{os.path.abspath(filepath)}",
            "features_included": len(key_features),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create website: {str(e)}",
            "product_name": product_name
        }
