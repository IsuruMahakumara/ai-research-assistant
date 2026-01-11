import os
from pinecone import Pinecone


class PineconeRetriever:
    def __init__(self, index_name: str, namespace: str):
        
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

        if not self.pc:
            raise ValueError("Pinecone API key is not set")
        
        self.index = self.pc.Index(index_name)
        self.namespace = namespace

    def search(self, query: str, top_k: int = 5, fields: list[str] = None):
        if fields is None:
            fields = ["text"]
        
        results = self.index.search(
            namespace=self.namespace,
            query={
                "inputs": {"text": query},
                "top_k": top_k
            },
            fields=fields
        )
        return results.to_dict()

