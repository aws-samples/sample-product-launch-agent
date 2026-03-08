from playwright.async_api import async_playwright
from bedrock_agentcore.tools.browser_client import BrowserClient
from rich.console import Console
import argparse
import asyncio
from boto3.session import Session

console = Console()
boto_session = Session()
region = boto_session.region_name

async def run_browser_task(prompt, region="us-east-1"):
    client = None
    try:
        console.print("[cyan]Starting AgentCore browser...[/cyan]")
        client = BrowserClient(region)
        client.start()
        
        ws_url, headers = client.generate_ws_headers()
        console.print("[green]✅ Browser started[/green]")
        
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(ws_url, headers=headers)
            context = browser.contexts[0]
            page = await context.new_page()
            page.set_default_timeout(60000)  # 60 second timeout
            
            console.print(f"[blue]🤖 Task:[/blue] {prompt}")
            
            if "bankrate" in prompt.lower():
                await page.goto("https://www.bankrate.com/loans/auto-loans/rates/", wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)  # Wait for content
                
                content = await page.content()
                if "auto loan" in content.lower():
                    console.print("[green]✅ Page loaded successfully[/green]")
                
                try:
                    rates = await page.locator("text=/\\d+\\.\\d+%/").all_text_contents()
                    console.print(f"[green]Found rates:[/green] {rates[:5]}")
                except:
                    console.print("[yellow]Could not extract rates, but page loaded[/yellow]")
            else:
                url = prompt.split("to ")[-1].split()[0]
                await page.goto(f"https://{url}", wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)
                title = await page.title()
                console.print(f"[green]Page:[/green] {title}")
            
            await page.screenshot(path="browser_result.png")
            console.print("[green]✅ Screenshot saved to browser_result.png[/green]")
            await browser.close()
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {e}")
    finally:
        if client:
            client.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--region", default="us-east-1")
    args = parser.parse_args()
    asyncio.run(run_browser_task(args.prompt, args.region))
