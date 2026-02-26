import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# The critical fix: Explicitly set version="v1"
embedder = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    version="v1",
)

try:
    vector = embedder.embed_query("Testing stable v1 endpoint")
    print(f"✅ Success! Vector size: {len(vector)}")
except Exception as e:
    # If the above still fails, try changing the model to "text-embedding-004" (no prefix)
    print(f"❌ Still failing: {e}")
