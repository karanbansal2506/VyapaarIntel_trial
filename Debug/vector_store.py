import chromadb
from chromadb.config import Settings
from google import genai
import os
import uuid

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class VectorStore:
    def __init__(self):
        self.chroma = chromadb.Client(
            Settings(persist_directory="./chroma_db")
        )
        self.collection = self.chroma.get_or_create_collection(
            name="reddit_comments"
        )

    def embed(self, text: str):
        res = client.models.embed_content(
            model="models/embedding-001",
            content=text
        )
        return res["embedding"]

    def add(self, text: str, metadata: dict):
        if not text.strip():
            return

        self.collection.add(
            ids=[str(uuid.uuid4())],
            documents=[text],
            embeddings=[self.embed(text)],
            metadatas=[metadata]
        )

    def search(self, query: str, k: int = 8):
        q_embed = self.embed(query)
        return self.collection.query(
            query_embeddings=[q_embed],
            n_results=k
        )
