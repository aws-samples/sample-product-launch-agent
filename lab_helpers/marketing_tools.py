import os
import json
import boto3
import base64
from typing import Dict, Any
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
from io import BytesIO
from strands.tools import tool

# Initialize Bedrock client for Nova Canvas
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))

@tool
def generate_marketing_image(prompt: str, style: str = "professional") -> Dict[str, Any]:
    """Generate marketing image using Amazon Nova Canvas with correct API format"""
    try:
        # Use correct Nova Canvas model ID and format from AWS docs
        model_id = "amazon.nova-canvas-v1:0"
        
        # Enhanced prompt for marketing materials - create actual marketing poster
        if 'personal loan' in prompt.lower():
            enhanced_prompt = f"Professional marketing poster for personal loans, clean modern design, blue and white corporate colors, financial services branding, include space for text overlay, professional banking aesthetic, trust-inspiring design"
        elif 'car loan' in prompt.lower() or 'auto loan' in prompt.lower():
            enhanced_prompt = f"Professional auto loan marketing poster, modern car financing design, blue and silver corporate colors, automotive financial services, clean professional layout, trust-inspiring banking design"
        elif 'home loan' in prompt.lower() or 'mortgage' in prompt.lower():
            enhanced_prompt = f"Professional home loan marketing poster, real estate financing design, blue and green corporate colors, mortgage services branding, clean professional layout, trust-inspiring design"
        else:
            enhanced_prompt = f"Professional financial services marketing poster, clean corporate design, blue and white gradient, modern banking aesthetic, professional layout, trust-inspiring financial branding"
        
        # Correct request format based on AWS Nova Canvas documentation
        request_body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": enhanced_prompt
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": "standard",
                "height": 1024,
                "width": 1024,
                "cfgScale": 8.0,
                "seed": 0
            }
        }
        
        # Invoke Nova Canvas model
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        if 'images' in response_body and len(response_body['images']) > 0:
            # Get base64 image data
            image_data = response_body['images'][0]
            
            # Save image
            image_filename = f"marketing_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            image_path = f"generated_materials/{image_filename}"
            
            # Create directories
            os.makedirs("generated_materials", exist_ok=True)
            os.makedirs("backend/generated_materials", exist_ok=True)
            
            # Decode and save image
            image_bytes = base64.b64decode(image_data)
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            
            # Also save in backend directory
            backend_path = f"backend/generated_materials/{image_filename}"
            with open(backend_path, 'wb') as f:
                f.write(image_bytes)
            
            return {
                "success": True,
                "image_path": image_path,
                "image_filename": image_filename,
                "prompt": enhanced_prompt,
                "model": "Nova Canvas",
                "timestamp": datetime.now().isoformat()
            }
        else:
            print("No images in Nova Canvas response, using fallback")
            return create_fallback_marketing_image(prompt, style)
            
    except Exception as e:
        print(f"Nova Canvas error: {str(e)}")
        # Always provide professional fallback
        return create_fallback_marketing_image(prompt, style)
    
    # For now, always use the professional fallback since Nova Canvas isn't producing good marketing content
    print("Using professional poster generator for better marketing content")
    return create_fallback_marketing_image(prompt, style)

def create_fallback_marketing_image(prompt: str, style: str) -> Dict[str, Any]:
    """Create a professional marketing poster when Nova Canvas fails"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import textwrap
        
        # Create a professional marketing poster
        width, height = 1024, 768
        
        # Create gradient background
        image = Image.new('RGB', (width, height), color='#ffffff')
        draw = ImageDraw.Draw(image)
        
        # Create a professional gradient background
        for i in range(height):
            # Blue gradient from top to bottom
            ratio = i / height
            r = int(25 + (100 - 25) * ratio)  # 25 to 100
            g = int(118 + (149 - 118) * ratio)  # 118 to 149  
            b = int(210 + (237 - 210) * ratio)  # 210 to 237
            color = (r, g, b)
            draw.line([(0, i), (width, i)], fill=color)
        
        # Add white overlay for better text readability
        overlay = Image.new('RGBA', (width, height), (255, 255, 255, 100))
        image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(image)
        
        # Try to use system fonts with better fallbacks
        try:
            font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
            font_subtitle = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            font_features = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
            font_cta = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 42)
            font_rate = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 64)
        except:
            try:
                font_title = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 72)
                font_subtitle = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
                font_features = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 28)
                font_cta = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 42)
                font_rate = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 64)
            except:
                font_title = ImageFont.load_default()
                font_subtitle = ImageFont.load_default()
                font_features = ImageFont.load_default()
                font_cta = ImageFont.load_default()
                font_rate = ImageFont.load_default()
        
        # Determine content based on the prompt
        if 'personal loan' in prompt.lower():
            title = "PERSONAL LOANS"
            subtitle = "Achieve Your Financial Goals"
            rate = "3.99% APR*"
            features = [
                "✓ Competitive Interest Rates",
                "✓ Quick Online Application", 
                "✓ Flexible Repayment Terms",
                "✓ No Hidden Fees"
            ]
            cta = "APPLY NOW"
        elif 'car loan' in prompt.lower() or 'auto loan' in prompt.lower():
            title = "AUTO LOANS"
            subtitle = "Drive Your Dreams Today"
            rate = "2.99% APR*"
            features = [
                "✓ Low Interest Rates",
                "✓ New & Used Vehicle Financing",
                "✓ Fast Approval Process", 
                "✓ Flexible Payment Options"
            ]
            cta = "GET PRE-APPROVED"
        elif 'home loan' in prompt.lower() or 'mortgage' in prompt.lower():
            title = "HOME LOANS"
            subtitle = "Your Dream Home Awaits"
            rate = "3.25% APR*"
            features = [
                "✓ Competitive Mortgage Rates",
                "✓ Expert Loan Officers",
                "✓ Quick Pre-Approval",
                "✓ First-Time Buyer Programs"
            ]
            cta = "START APPLICATION"
        else:
            title = prompt.replace('_', ' ').upper()
            subtitle = "Professional Financial Solutions"
            rate = "3.99% APR*"
            features = [
                "✓ Competitive Rates",
                "✓ Fast Approval Process",
                "✓ Excellent Customer Service",
                "✓ Trusted Financial Partner"
            ]
            cta = "APPLY TODAY"
        
        # Add company logo area (top)
        draw.rectangle([(0, 0), (width, 80)], fill='#1976d2')
        draw.text((50, 25), "PREMIER FINANCIAL", fill='white', font=font_subtitle)
        
        # Add main title
        title_bbox = draw.textbbox((0, 0), title, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 120), title, fill='#1976d2', font=font_title)
        
        # Add subtitle
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        draw.text((subtitle_x, 200), subtitle, fill='#333333', font=font_subtitle)
        
        # Add rate in a prominent box
        rate_box_y = 280
        rate_box_height = 100
        draw.rectangle([(150, rate_box_y), (width-150, rate_box_y + rate_box_height)], 
                      fill='#ff6b35', outline='#e55a2b', width=3)
        
        rate_bbox = draw.textbbox((0, 0), rate, font=font_rate)
        rate_width = rate_bbox[2] - rate_bbox[0]
        rate_x = (width - rate_width) // 2
        draw.text((rate_x, rate_box_y + 20), rate, fill='white', font=font_rate)
        
        # Add "Starting Rate" text
        starting_text = "Starting Rate"
        starting_bbox = draw.textbbox((0, 0), starting_text, font=font_features)
        starting_width = starting_bbox[2] - starting_bbox[0]
        starting_x = (width - starting_width) // 2
        draw.text((starting_x, rate_box_y + rate_box_height + 10), starting_text, fill='#666666', font=font_features)
        
        # Add features
        features_start_y = 450
        for i, feature in enumerate(features):
            y_pos = features_start_y + (i * 40)
            draw.text((100, y_pos), feature, fill='#333333', font=font_features)
        
        # Add call-to-action button
        cta_y = 620
        cta_box_height = 60
        draw.rectangle([(200, cta_y), (width-200, cta_y + cta_box_height)], 
                      fill='#4caf50', outline='#45a049', width=3)
        
        cta_bbox = draw.textbbox((0, 0), cta, font=font_cta)
        cta_width = cta_bbox[2] - cta_bbox[0]
        cta_x = (width - cta_width) // 2
        draw.text((cta_x, cta_y + 10), cta, fill='white', font=font_cta)
        
        # Add disclaimer at bottom
        disclaimer = "*Rate shown for qualified applicants. Terms and conditions apply."
        draw.text((50, height - 40), disclaimer, fill='#888888', font=ImageFont.load_default())
        
        # Save image
        image_filename = f"marketing_poster_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        image_path = f"generated_materials/{image_filename}"
        
        # Create directories
        os.makedirs("generated_materials", exist_ok=True)
        os.makedirs("backend/generated_materials", exist_ok=True)
        
        # Save image
        image.save(image_path, quality=95, optimize=True)
        image.save(f"backend/generated_materials/{image_filename}", quality=95, optimize=True)
        
        return {
            "success": True,
            "image_path": image_path,
            "image_filename": image_filename,
            "prompt": prompt,
            "model": "Professional Poster Generator",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Professional poster creation failed: {str(e)}",
            "prompt": prompt
        }

@tool
def create_marketing_poster(product_name: str, catchphrase: str, image_prompt: str, logo_text: str = "FinanceAI") -> Dict[str, Any]:
    """Create marketing poster with single Nova Canvas image and professional PDF with Instagram/Google ad styling"""
    try:
        print(f"🎨 Creating marketing poster for: {product_name}")
        
        # Step 1: Generate ONLY ONE image using Nova Canvas
        image_data = None
        image_source = "fallback"
        
        try:
            print("📸 Attempting Nova Canvas image generation...")
            # Enhanced prompt for clean background image without text
            clean_prompt = f"Professional financial services background image, {image_prompt}, clean minimalist design, corporate gradient background, no text, no logos, suitable for overlay text, high quality, modern aesthetic"
            
            model_id = "amazon.nova-canvas-v1:0"
            
            # Correct Nova Canvas API format - generate exactly 1 image
            request_body = {
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": clean_prompt
                },
                "imageGenerationConfig": {
                    "numberOfImages": 1,  # Explicitly set to 1
                    "quality": "standard",
                    "height": 1024,
                    "width": 1024,
                    "cfgScale": 8.0,
                    "seed": 42  # Fixed seed for consistency
                }
            }
            
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            
            if 'images' in response_body and len(response_body['images']) > 0:
                # Take only the first image (should be only one anyway)
                image_data = base64.b64decode(response_body['images'][0])
                image_source = "Nova Canvas"
                print("✅ Nova Canvas image generated successfully")
            else:
                raise Exception("No images in Nova Canvas response")
                
        except Exception as nova_error:
            print(f"❌ Nova Canvas failed: {nova_error}")
            print("🔄 Using professional fallback image generator...")
            
            # Create professional fallback image
            fallback_result = create_fallback_marketing_image(product_name, "professional")
            if fallback_result["success"]:
                with open(fallback_result["image_path"], 'rb') as f:
                    image_data = f.read()
                image_source = "Professional Generator"
                print("✅ Fallback image created successfully")
            else:
                raise Exception("Both Nova Canvas and fallback image generation failed")

        # Step 2: Create timestamp and filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"marketing_image_{timestamp}.png"
        pdf_filename = f"marketing_poster_{timestamp}.pdf"
        
        # Create directories
        os.makedirs("generated_materials", exist_ok=True)
        os.makedirs("backend/generated_materials", exist_ok=True)
        
        # Save the single image
        image_path = os.path.join("generated_materials", image_filename)
        backend_image_path = os.path.join("backend/generated_materials", image_filename)
        
        with open(image_path, 'wb') as f:
            f.write(image_data)
        with open(backend_image_path, 'wb') as f:
            f.write(image_data)
        
        print(f"💾 Image saved: {image_filename}")
        
        # Step 3: Create Instagram/Google Ad style PDF
        pdf_path = os.path.join("generated_materials", pdf_filename)
        backend_pdf_path = os.path.join("backend/generated_materials", pdf_filename)
        
        # Generate marketing content based on product type
        if 'personal loan' in product_name.lower():
            headline = "Get Your Personal Loan Today"
            benefits = ["✓ Rates as low as 3.99% APR", "✓ Quick 5-minute application", "✓ Same-day approval", "✓ No hidden fees"]
            cta = "APPLY NOW"
            rate_text = "3.99% APR*"
        elif 'car loan' in product_name.lower() or 'auto' in product_name.lower():
            headline = "Finance Your Dream Car"
            benefits = ["✓ Rates from 2.99% APR", "✓ New & used vehicles", "✓ Fast pre-approval", "✓ Flexible terms"]
            cta = "GET PRE-APPROVED"
            rate_text = "2.99% APR*"
        elif 'home loan' in product_name.lower() or 'mortgage' in product_name.lower():
            headline = "Your Dream Home Awaits"
            benefits = ["✓ Competitive rates from 3.25%", "✓ Expert loan officers", "✓ First-time buyer programs", "✓ Quick pre-approval"]
            cta = "START APPLICATION"
            rate_text = "3.25% APR*"
        else:
            headline = f"Discover {product_name}"
            benefits = ["✓ Competitive rates", "✓ Fast approval process", "✓ Excellent service", "✓ Trusted partner"]
            cta = "LEARN MORE"
            rate_text = "Great Rates*"
        
        # Create Instagram/Google Ad style PDF
        for path in [pdf_path, backend_pdf_path]:
            c = canvas.Canvas(path, pagesize=(612, 792))  # Standard letter size
            width, height = 612, 792
            
            # Background image (full bleed)
            c.drawImage(image_path, 0, 0, width=width, height=height, preserveAspectRatio=True, mask='auto')
            
            # Instagram/Google Ad style overlay design
            # Top brand bar (like Instagram ads)
            c.setFillColor(HexColor('#1976D2'))
            c.setFillAlpha(0.95)
            c.rect(0, height-80, width, 80, fill=1, stroke=0)
            
            # Brand text
            c.setFillColor(HexColor('#FFFFFF'))
            c.setFillAlpha(1)
            c.setFont("Helvetica-Bold", 18)
            c.drawString(20, height-50, logo_text.upper())
            c.setFont("Helvetica", 12)
            c.drawString(20, height-65, "Financial Services")
            
            # Main content area with gradient overlay (like Google ads)
            # Create gradient effect with multiple rectangles
            overlay_start = height * 0.45
            overlay_height = height * 0.4
            
            for i in range(20):
                alpha = 0.05 + (i * 0.02)  # Gradual opacity increase
                c.setFillColor(HexColor('#000000'))
                c.setFillAlpha(alpha)
                rect_height = overlay_height / 20
                c.rect(0, overlay_start + (i * rect_height), width, rect_height, fill=1, stroke=0)
            
            # Main headline (Instagram ad style)
            c.setFillColor(HexColor('#FFFFFF'))
            c.setFillAlpha(1)
            c.setFont("Helvetica-Bold", 32)
            
            # Center the headline
            headline_width = c.stringWidth(headline, "Helvetica-Bold", 32)
            headline_x = (width - headline_width) / 2
            c.drawString(headline_x, height * 0.65, headline)
            
            # Catchphrase
            c.setFont("Helvetica", 18)
            catchphrase_width = c.stringWidth(catchphrase, "Helvetica", 18)
            catchphrase_x = (width - catchphrase_width) / 2
            c.drawString(catchphrase_x, height * 0.6, catchphrase)
            
            # Rate highlight box (Google ad style)
            rate_box_width = 200
            rate_box_height = 60
            rate_box_x = (width - rate_box_width) / 2
            rate_box_y = height * 0.52
            
            c.setFillColor(HexColor('#FF6B35'))
            c.setFillAlpha(0.95)
            c.roundRect(rate_box_x, rate_box_y, rate_box_width, rate_box_height, 8, fill=1, stroke=0)
            
            c.setFillColor(HexColor('#FFFFFF'))
            c.setFillAlpha(1)
            c.setFont("Helvetica-Bold", 24)
            rate_width = c.stringWidth(rate_text, "Helvetica-Bold", 24)
            rate_x = rate_box_x + (rate_box_width - rate_width) / 2
            c.drawString(rate_x, rate_box_y + 20, rate_text)
            
            # Benefits list (Instagram story style)
            c.setFont("Helvetica", 14)
            benefits_start_y = height * 0.42
            for i, benefit in enumerate(benefits[:4]):
                benefit_y = benefits_start_y - (i * 25)
                benefit_width = c.stringWidth(benefit, "Helvetica", 14)
                benefit_x = (width - benefit_width) / 2
                c.drawString(benefit_x, benefit_y, benefit)
            
            # Call-to-action button (Google ad style)
            cta_button_width = 250
            cta_button_height = 50
            cta_button_x = (width - cta_button_width) / 2
            cta_button_y = height * 0.15
            
            c.setFillColor(HexColor('#4CAF50'))
            c.setFillAlpha(0.95)
            c.roundRect(cta_button_x, cta_button_y, cta_button_width, cta_button_height, 25, fill=1, stroke=0)
            
            # CTA button border (like social media ads)
            c.setStrokeColor(HexColor('#45A049'))
            c.setLineWidth(2)
            c.roundRect(cta_button_x, cta_button_y, cta_button_width, cta_button_height, 25, fill=0, stroke=1)
            
            c.setFillColor(HexColor('#FFFFFF'))
            c.setFillAlpha(1)
            c.setFont("Helvetica-Bold", 18)
            cta_width = c.stringWidth(cta, "Helvetica-Bold", 18)
            cta_x = cta_button_x + (cta_button_width - cta_width) / 2
            c.drawString(cta_x, cta_button_y + 16, cta)
            
            # Footer disclaimer (required for financial ads)
            c.setFont("Helvetica", 8)
            c.setFillColor(HexColor('#888888'))
            disclaimer = "*Rates shown for qualified applicants. Terms and conditions apply. Subject to credit approval."
            disclaimer_width = c.stringWidth(disclaimer, "Helvetica", 8)
            disclaimer_x = (width - disclaimer_width) / 2
            c.drawString(disclaimer_x, 30, disclaimer)
            
            # Social media style corner elements
            c.setFillColor(HexColor('#FFFFFF'))
            c.setFillAlpha(0.8)
            c.circle(width-30, 30, 15, fill=1, stroke=0)  # Like button placeholder
            
            c.save()
        
        print(f"📄 PDF created: {pdf_filename}")
        
        return {
            "success": True,
            "message": f"✅ Marketing poster created for {product_name}! Single {image_source} image with Instagram/Google ad styling.",
            "pdf_filename": pdf_filename,
            "image_filename": image_filename,
            "pdf_url": f"/materials/{pdf_filename}",
            "image_url": f"/materials/{image_filename}",
            "image_source": image_source,
            "ad_style": "Instagram/Google Ad Format",
            "timestamp": timestamp,
            "session_files": {
                "pdf": pdf_filename,
                "image": image_filename
            }
        }
        
    except Exception as e:
        print(f"❌ Marketing poster creation failed: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to create marketing poster: {str(e)}",
            "product_name": product_name
        }

@tool
def create_social_media_campaign(product_name: str, target_audience: str) -> Dict[str, Any]:
    """Create social media marketing materials using Nova Canvas"""
    try:
        campaigns = []
        
        # Different social media formats
        formats = [
            {"name": "Instagram Post", "size": "1080x1080", "style": "vibrant social media"},
            {"name": "Facebook Banner", "size": "1200x630", "style": "professional facebook cover"},
            {"name": "LinkedIn Post", "size": "1200x627", "style": "corporate linkedin professional"}
        ]
        
        for format_info in formats:
            prompt = f"{product_name} for {target_audience}, {format_info['style']}, modern design, financial services"
            
            image_result = generate_marketing_image(prompt, format_info['style'])
            
            if image_result.get("success"):
                campaigns.append({
                    "platform": format_info["name"],
                    "image_path": image_result["image_path"],
                    "size": format_info["size"],
                    "prompt": prompt
                })
        
        return {
            "success": True,
            "campaigns": campaigns,
            "product_name": product_name,
            "target_audience": target_audience,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Campaign creation error: {str(e)}"
        }
