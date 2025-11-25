from bedrock_agentcore.runtime import BedrockAgentCoreApp
import os
import sys
import traceback
from dotenv import load_dotenv

load_dotenv()

app = BedrockAgentCoreApp()

# Initialize orchestrator with detailed error handling
orchestrator = None
init_error = None

try:
    print("=" * 60)
    print("Initializing Financial Product Agent...")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"TAVILY_API_KEY present: {bool(os.getenv('TAVILY_API_KEY'))}")
    print(f"BEDROCK_MODEL_ID: {os.getenv('BEDROCK_MODEL_ID', 'not set')}")
    print("=" * 60)
    
    from ai_multi_agent_system import get_ai_orchestrator_agent
    orchestrator = get_ai_orchestrator_agent()
    print("✅ Orchestrator initialized successfully!")
    
except Exception as e:
    init_error = str(e)
    print(f"❌ Failed to initialize orchestrator: {e}")
    print("Traceback:")
    traceback.print_exc()
    print("=" * 60)

def extract_content(response):
    """Extract text content from various response formats"""
    try:
        if hasattr(response, 'message'):
            message = response.message
            
            # Handle dict format with content array
            if isinstance(message, dict) and 'content' in message:
                content = message['content']
                if isinstance(content, list) and len(content) > 0:
                    if isinstance(content[0], dict) and 'text' in content[0]:
                        return content[0]['text']
                    else:
                        return str(content[0])
                else:
                    return str(content)
            
            # Handle direct string message
            elif isinstance(message, str):
                return message
            
            # Handle other message formats
            else:
                return str(message)
        
        # Fallback to string conversion
        return str(response)
        
    except Exception as e:
        return f"Error extracting content: {str(e)}"

@app.entrypoint
def invoke(payload):
    try:
        user_message = payload.get("prompt", "Hello")
        print(f"\n📥 Received request: {user_message[:100]}...")
        
        if orchestrator is None:
            error_msg = f"Agent not initialized. Error: {init_error}" if init_error else "Agent initialization in progress"
            print(f"⚠️  {error_msg}")
            return {"result": error_msg, "status": "initializing"}
        
        print("🤖 Calling orchestrator...")
        # Call agent directly
        response = orchestrator(user_message)
        
        # Extract content using improved handler
        content = extract_content(response)
        print(f"✅ Response generated: {content[:100]}...")
        return {"result": content}
        
    except Exception as e:
        error_msg = f"Runtime error: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        return {"error": error_msg}

if __name__ == "__main__":
    print("🚀 Starting BedrockAgentCore app...")
    app.run()
