import chromadb
from chromadb.utils import embedding_functions
import config 
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChromaDBManager:
    
    def __init__(self):
        logging.info("Initializing ChromaDB Manager...")
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        self.client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection(
            name=config.CHROMA_COLLECTION_NAME,
            embedding_function=self.embedding_function
        )
        logging.info(f"Connected to ChromaDB collection: '{config.CHROMA_COLLECTION_NAME}'")

    def store_version(self, text_content: str, metadata: dict) -> str:
        doc_id = f"chapter-v{metadata['version']}"
        
        logging.info(f"Storing document with ID: {doc_id} and metadata: {metadata}")

        try:
            self.collection.add(
                documents=[text_content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logging.info(f"Successfully stored version {metadata['version']}.")
            return doc_id
        except Exception as e:
            logging.error(f"Error storing version: {e}")
            return None

    def get_latest_version(self) -> tuple[dict, str, str]:
        try:
            all_docs = self.collection.get(include=["metadatas", "documents"])
            
            if not all_docs or not all_docs['ids']:
                logging.info("Collection is empty. No versions found.")
                return None, None, None
            
            latest_doc_index = max(
                range(len(all_docs['metadatas'])),
                key=lambda i: all_docs['metadatas'][i].get('version', 0)
            )
            
            latest_metadata = all_docs['metadatas'][latest_doc_index]
            latest_document = all_docs['documents'][latest_doc_index]
            latest_id = all_docs['ids'][latest_doc_index]

            logging.info(f"Retrieved latest version: {latest_metadata.get('version', 'N/A')}")
            return latest_metadata, latest_document, latest_id
        except Exception as e:
            logging.error(f"Error getting latest version: {e}")
            return None, None, None

    def semantic_search(self, query: str, num_results: int = 3) -> list:
        logging.info(f"Performing semantic search for: '{query}'")
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=num_results,
                include=["documents", "metadatas", "distances"]
            )

            formatted_results = []
            for i, distance in enumerate(results['distances'][0]):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "distance": f"{distance:.4f}", 
                    "metadata": results['metadatas'][0][i],
                    "content": results['documents'][0][i][:250] + "..." 
                })
                
            logging.info(f"Found {len(formatted_results)} results.")
            return formatted_results
        except Exception as e:
            logging.error(f"Error during semantic search: {e}")
            return []