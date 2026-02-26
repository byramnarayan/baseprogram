import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from langchain_qdrant import QdrantVectorStore
from langchain_core.embeddings import Embeddings

load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiEmbeddings(Embeddings):
    """Custom embeddings using models/gemini-embedding-001"""

    def embed_documents(self, texts):
        """Embed documents for indexing"""
        embeddings = []
        for text in texts:
            result = client.models.embed_content(
                model="models/gemini-embedding-001",
                contents=text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            )
            embeddings.append(result.embeddings[0].values)
        return embeddings

    def embed_query(self, text):
        """Embed query for searching"""
        result = client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
        )
        return result.embeddings[0].values


# Initialize embeddings
embedding_model = GeminiEmbeddings()

# Connect to existing vector database
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_rag",
    embedding=embedding_model,
)

# Take user input
user_query = input("Ask something: ")

# Get relevant chunks from vector database
search_results = vector_db.similarity_search(query=user_query, k=35)

# Build context from search results
context = "\n\n\n".join(
    [
        f"Page Content: {result.page_content}\n"
        f"Page Number: {result.metadata.get('page', 'N/A')}\n"
        f"File Location: {result.metadata.get('source', 'N/A')}"
        for result in search_results
    ]
)

# System prompt
SYSTEM_PROMPT = f"""
You are a helpful AI Assistant who 
answers user queries based on the available context retrieved from PDF files along with page contents and page numbers.
You should only answer the user based on the following context and navigate the user to open the right page number to know more.

Context:
{context}
"""

# Generate response using Gemini
response = client.models.generate_content(
    model="models/gemini-2.5-flash",
    contents=[
        types.Content(
            role="user",
            parts=[types.Part(text=SYSTEM_PROMPT + "\n\nUser Question: " + user_query)],
        )
    ],
)

print(f"🤖: {response.text}")
    