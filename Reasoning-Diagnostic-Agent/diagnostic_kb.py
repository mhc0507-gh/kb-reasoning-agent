import chromadb

from sentence_transformers import SentenceTransformer
from diagnostic_docs import sample_documents

class DiagnosticKB:
    def __init__(self):
        # RAG configuration
        self.sample_documents = sample_documents

        # Initialize RAG components
        self.initialize_rag()


    def initialize_rag(self):
        """Initialize RAG components including ChromaDB and sentence transformer"""
        try:
            # Initialize sentence transformer model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

            # Initialize ChromaDB client
            self.chroma_client = chromadb.Client()

            # Create or get collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="knowledge_base",
                metadata={"hnsw:space": "cosine"}
            )

            # Add documents to collection
            self.add_documents_to_collection()

        except Exception as e:
            print(f"Error initializing RAG: {str(e)}")


    def add_documents_to_collection(self):
        """Add sample documents to ChromaDB collection"""
        try:
            # Generate embeddings for documents
            embeddings = self.embedding_model.encode(self.sample_documents)

            # Prepare documents for ChromaDB
            documents = []
            metadatas = []
            ids = []

            for i, doc in enumerate(self.sample_documents):
                documents.append(doc)
                metadatas.append({"source": "sample_document", "index": i})
                ids.append(f"doc_{i}")

            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings.tolist(),
                metadatas=metadatas,
                ids=ids
            )

        except Exception as e:
            print(f"Error adding documents to collection: {str(e)}")


    def query_rag(self, query, n_results=2):
        """Query the RAG system to retrieve relevant documents"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])

            # Query the collection
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results
            )

            # Extract relevant documents
            relevant_docs = results['documents'][0] if results['documents'] else []

            return relevant_docs

        except Exception as e:
            print(f"Error querying RAG: {str(e)}")
            return []
