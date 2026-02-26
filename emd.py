import os
import time
from pathlib import Path
from dotenv import load_dotenv
from tenacity import retry, wait_random_exponential, stop_after_attempt

from google import genai
from google.genai import types
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_core.embeddings import Embeddings

load_dotenv()

# --- CONFIGURATION ---
BOOKS_DIR = Path(__file__).parent / "book"
BATCH_SIZE = 5
COLLECTION_NAME = "agri"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize client
client = genai.Client(api_key=GEMINI_API_KEY)


class GeminiEmbeddings(Embeddings):
    """Custom embeddings using models/gemini-embedding-001"""
    
    def embed_documents(self, texts):
        """Embed documents for indexing"""
        embeddings = []
        for text in texts:
            result = client.models.embed_content(
                model="models/gemini-embedding-001",
                contents=text,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT"
                )
            )
            embeddings.append(result.embeddings[0].values)
        return embeddings
    
    def embed_query(self, text):
        """Embed query for searching"""
        result = client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY"
            )
        )
        return result.embeddings[0].values


embeddings = GeminiEmbeddings()


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def add_to_vectorstore(vector_store, documents):
    vector_store.add_documents(documents)


def main():
    pdf_files = list(BOOKS_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {BOOKS_DIR}")
        return

    print(f"Found {len(pdf_files)} files. Connecting to Qdrant...")

    vector_store = QdrantVectorStore.from_documents(
        documents=[],
        embedding=embeddings,
        url="http://localhost:6333",
        collection_name=COLLECTION_NAME,
    )

    for pdf_path in pdf_files:
        print(f"\n--- Processing: {pdf_path.name} ---")
        loader = PyPDFLoader(file_path=str(pdf_path))
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        chunks = text_splitter.split_documents(docs)
        print(f"Created {len(chunks)} chunks")

        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i : i + BATCH_SIZE]
            try:
                add_to_vectorstore(vector_store, batch)
                print(f"✓ Batch {i // BATCH_SIZE + 1}/{(len(chunks)-1)//BATCH_SIZE + 1}")
                time.sleep(3)
            except Exception as e:
                print(f"✗ Batch {i // BATCH_SIZE + 1} failed: {e}")

    print("\n[SUCCESS] Indexing complete.")


if __name__ == "__main__":
    main()