from typing import List, Dict, Any
import openai
from config.settings import OPENAI_API_KEY, CHAT_MODEL, MAX_CONTEXT_LENGTH, TOP_K_RESULTS
from src.database.supabase_client import SupabaseClient
from src.embeddings.embeddings_service import EmbeddingsService

class ChatService:
    """
    Service for handling chat interactions with the PDF documents
    """
    
    def __init__(self):
        """Initialize the chat service with dependencies"""
        openai.api_key = OPENAI_API_KEY
        self.db_client = SupabaseClient()
        self.embeddings_service = EmbeddingsService()
        self.model = CHAT_MODEL
    
    def get_relevant_context(self, query: str) -> str:
        """
        Get relevant context from the database based on the query
        
        Args:
            query: User query
            
        Returns:
            str: Relevant context from documents
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embeddings_service.generate_query_embedding(query)
            
            # Perform similarity search
            results = self.db_client.similarity_search(query_embedding, TOP_K_RESULTS)
            
            # Debug: Print out the results
            print(f"Retrieved {len(results)} results from similarity search")
            
            # Extract and combine the text from the results
            context_parts = []
            for result in results:
                # Debug: Print each result's similarity score
                print(f"Similarity: {result.get('similarity', 'N/A')}")
                
                # Handle different result structures
                content = result.get('content')
                if not content and isinstance(result, dict):
                    # Try to get content from different fields
                    content = result.get('text', '')
                
                # Get metadata
                metadata = result.get('metadata', {})
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {"source": "unknown"}
                
                filename = metadata.get('filename', 'unknown_file')
                context_parts.append(f"Document: {filename}\n{content}")
            
            context = "\n\n".join(context_parts)
            
            # Debug: Print context length
            print(f"Context length: {len(context)} characters")
            
            return context
        except Exception as e:
            print(f"Error in get_relevant_context: {str(e)}")
            raise Exception(f"Error retrieving context: {str(e)}")
    
    def generate_answer(self, query: str, context: str) -> str:
        """
        Generate an answer to the user query based on the provided context
        
        Args:
            query: User query
            context: Relevant context from documents
            
        Returns:
            str: Generated answer
        """
        try:
            # Check if context is empty
            if not context or context.strip() == "":
                return "I don't have enough information to answer that question based on the documents you've uploaded."
            
            # Truncate context if it's too long
            if len(context) > MAX_CONTEXT_LENGTH:
                context = context[:MAX_CONTEXT_LENGTH]
            
            # Create the prompt for the language model
            system_prompt = (
                "You are a helpful assistant that answers questions based on the provided document context. "
                "If the answer cannot be found in the context, say that you don't know. "
                "Don't make up information. Provide accurate answers based only on the context given."
            )
            
            user_prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
            
            # Make the API call
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in generate_answer: {str(e)}")
            raise Exception(f"Error generating answer: {str(e)}")
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query and generate a response
        
        Args:
            query: User query
            
        Returns:
            Dict: Response with answer and sources
        """
        try:
            import json
            
            # Get relevant context
            context = self.get_relevant_context(query)
            
            # Generate answer
            answer = self.generate_answer(query, context)
            
            return {
                "answer": answer,
                "context": context
            }
        except Exception as e:
            print(f"Error in process_query: {str(e)}")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "context": ""
            }


# from typing import List, Dict, Any
# import openai
# from config.settings import OPENAI_API_KEY, CHAT_MODEL, MAX_CONTEXT_LENGTH, TOP_K_RESULTS
# from src.database.supabase_client import SupabaseClient
# from src.embeddings.embeddings_service import EmbeddingsService

# class ChatService:
#     """
#     Service for handling chat interactions with the PDF documents
#     """
    
#     def __init__(self):
#         """Initialize the chat service with dependencies"""
#         openai.api_key = OPENAI_API_KEY
#         self.db_client = SupabaseClient()
#         self.embeddings_service = EmbeddingsService()
#         self.model = CHAT_MODEL
    
#     def get_relevant_context(self, query: str) -> str:
#         """
#         Get relevant context from the database based on the query
        
#         Args:
#             query: User query
            
#         Returns:
#             str: Relevant context from documents
#         """
#         try:
#             # Generate embedding for the query
#             query_embedding = self.embeddings_service.generate_query_embedding(query)
            
#             # Perform similarity search
#             results = self.db_client.similarity_search(query_embedding, TOP_K_RESULTS)
            
#             # Extract and combine the text from the results
#             context_parts = []
#             for result in results:
#                 context_parts.append(f"Document: {result['metadata']['filename']}\n{result['content']}")
            
#             return "\n\n".join(context_parts)
#         except Exception as e:
#             raise Exception(f"Error retrieving context: {str(e)}")
    
#     def generate_answer(self, query: str, context: str) -> str:
#         """
#         Generate an answer to the user query based on the provided context
        
#         Args:
#             query: User query
#             context: Relevant context from documents
            
#         Returns:
#             str: Generated answer
#         """
#         try:
#             # Truncate context if it's too long
#             if len(context) > MAX_CONTEXT_LENGTH:
#                 context = context[:MAX_CONTEXT_LENGTH]
            
#             # Create the prompt for the language model
#             system_prompt = (
#                 "You are a helpful assistant that answers questions based on the provided document context. "
#                 "If the answer cannot be found in the context, say that you don't know. "
#                 "Don't make up information. Provide accurate answers based only on the context given."
#             )
            
#             user_prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
            
#             # Make the API call
#             response = openai.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {"role": "system", "content": system_prompt},
#                     {"role": "user", "content": user_prompt}
#                 ],
#                 temperature=0.3,
#                 max_tokens=1000
#             )
            
#             return response.choices[0].message.content
#         except Exception as e:
#             raise Exception(f"Error generating answer: {str(e)}")
    
#     def process_query(self, query: str) -> Dict[str, Any]:
#         """
#         Process a user query and generate a response
        
#         Args:
#             query: User query
            
#         Returns:
#             Dict: Response with answer and sources
#         """
#         try:
#             # Get relevant context
#             context = self.get_relevant_context(query)
            
#             # Generate answer
#             answer = self.generate_answer(query, context)
            
#             return {
#                 "answer": answer,
#                 "context": context
#             }
#         except Exception as e:
#             raise Exception(f"Error processing query: {str(e)}")