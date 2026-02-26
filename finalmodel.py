import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Fetching available models...")
print("=" * 60)

for model in client.models.list():
    print(f"\nModel: {model.name}")
    print(f"  Display name: {model.display_name}")
    print(
        f"  Description: {model.description[:100] if model.description else 'N/A'}..."
    )

print("\n" + "=" * 60)
print("For embedding, try these model names:")
print("  - text-embedding-004")
print("  - embedding-001")
print("=" * 60)
