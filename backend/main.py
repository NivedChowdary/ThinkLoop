import anthropic
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Claude client
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

def test_jamie():
    """Test if Jamie (our intake agent) is working"""
    
    print("🤖 Calling Jamie...")
    
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        messages=[
            {
                "role": "user", 
                "content": """You are Jamie, the Intake Specialist for ThinkLoop.

Your personality:
- Detail-oriented and thorough
- Friendly but professional
- You ask good clarifying questions
- You never forget what the client said

The user just said: "Hey Jamie, I need to hire a Python developer"

Respond as Jamie would. Be enthusiastic and helpful!"""
            }
        ]
    )
    
    print("\n" + "="*60)
    print("🎉 JAMIE SAYS:")
    print("="*60)
    print(message.content[0].text)
    print("="*60)
    print("\n✅ SUCCESS! Claude API is working!")
    print("✅ Jamie is ALIVE!")

if __name__ == "__main__":
    test_jamie()