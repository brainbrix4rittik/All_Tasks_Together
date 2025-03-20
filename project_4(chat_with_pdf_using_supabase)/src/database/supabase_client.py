from typing import List, Dict, Any
from supabase import create_client
import json
from config.settings import SUPABASE_URL, SUPABASE_KEY, VECTOR_COLLECTION_NAME

class SupabaseClient:
    """
    Client for interacting with Supabase vector database
    """
    
    def __init__(self):
        """Initialize Supabase client with credentials"""
        self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.table_name = VECTOR_COLLECTION_NAME
    
    def store_document_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Store document chunks with embeddings in Supabase
        
        Args:
            chunks: List of chunks with embeddings
            
        Returns:
            bool: Success status
        """
        try:
            for chunk in chunks:
                chunk_data = {
                    "id": chunk["id"],
                    "content": chunk["text"],
                    "embedding": chunk["embedding"],
                    "metadata": json.dumps(chunk["metadata"]) if isinstance(chunk["metadata"], dict) else chunk["metadata"]
                }
                
                result = self.client.table(self.table_name).insert(chunk_data).execute()
                
                # Safely check the response
                if hasattr(result, 'data') and result.data:
                    print(f"Inserted chunk {chunk['id']} successfully.")
                else:
                    print(f"Failed to insert chunk {chunk['id']}: {result}")
            
            return True
        except Exception as e:
            print(f"Error storing chunks in Supabase: {str(e)}")
            raise Exception(f"Error storing chunks in Supabase: {str(e)}")

    
    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform similarity search using vector embedding
        
        Args:
            query_embedding: Vector embedding of the query
            top_k: Number of top results to return
            
        Returns:
            List[Dict]: Similar document chunks
        """
        try:
            print(f"Performing similarity search with top_k={top_k}")
            
            # Try with a more lenient threshold
            response = self.client.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_count": top_k,
                    "match_threshold": 0.1  # Lower threshold to get more results
                }
            ).execute()
            
            if not response.data:
                print("No results from similarity search, trying direct table query")
                # Fallback: If no results, try to get the most recent documents
                fallback = self.client.table(self.table_name).select("*").limit(top_k).execute()
                return fallback.data
                
            return response.data
        except Exception as e:
            print(f"Error in similarity search: {str(e)}")
            # Fallback: return an empty list instead of raising an exception
            return []
    
    def get_document_by_id(self, doc_id: str) -> Dict[str, Any]:
        """
        Retrieve a document by ID
        
        Args:
            doc_id: Document ID
            
        Returns:
            Dict: Document data
        """
        try:
            response = self.client.table(self.table_name).select("*").eq("id", doc_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error retrieving document: {str(e)}")
            return None


# from typing import List, Dict, Any
# from supabase import create_client
# from config.settings import SUPABASE_URL, SUPABASE_KEY, VECTOR_COLLECTION_NAME

# class SupabaseClient:
#     """
#     Client for interacting with Supabase vector database
#     """
    
#     def __init__(self):
#         """Initialize Supabase client with credentials"""
#         self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
#         self.table_name = VECTOR_COLLECTION_NAME
    
#     def store_document_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
#         """
#         Store document chunks with embeddings in Supabase
        
#         Args:
#             chunks: List of chunks with embeddings
            
#         Returns:
#             bool: Success status
#         """
#         try:
#             for chunk in chunks:
#                 chunk_data = {
#                     "id": chunk["id"],
#                     "content": chunk["text"],
#                     "embedding": chunk["embedding"],
#                     "metadata": chunk["metadata"]
#                 }
                
#                 self.client.table(self.table_name).insert(chunk_data).execute()
            
#             return True
#         except Exception as e:
#             raise Exception(f"Error storing chunks in Supabase: {str(e)}")
    
#     def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
#         """
#         Perform similarity search using vector embedding
        
#         Args:
#             query_embedding: Vector embedding of the query
#             top_k: Number of top results to return
            
#         Returns:
#             List[Dict]: Similar document chunks
#         """
#         try:
#             response = self.client.rpc(
#                 "match_documents",
#                 {
#                     "query_embedding": query_embedding,
#                     "match_count": top_k
#                 }
#             ).execute()
            
#             return response.data
#         except Exception as e:
#             raise Exception(f"Error performing similarity search: {str(e)}")
    
#     def get_document_by_id(self, doc_id: str) -> Dict[str, Any]:
#         """
#         Retrieve a document by ID
        
#         Args:
#             doc_id: Document ID
            
#         Returns:
#             Dict: Document data
#         """
#         try:
#             response = self.client.table(self.table_name).select("*").eq("id", doc_id).execute()
#             if response.data and len(response.data) > 0:
#                 return response.data[0]
#             return None
#         except Exception as e:
#             raise Exception(f"Error retrieving document: {str(e)}")