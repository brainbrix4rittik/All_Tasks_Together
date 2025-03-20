import streamlit as st
from src.ui.components import UIComponents
from src.pdf.pdf_processor import PDFProcessor
from src.embeddings.embeddings_service import EmbeddingsService
from src.database.supabase_client import SupabaseClient
from src.chat.chat_service import ChatService

class AppPages:
    """
    Class containing the main pages and logic for the Streamlit application
    """
    
    def __init__(self):
        """Initialize app dependencies"""
        self.pdf_processor = PDFProcessor()
        self.embedding_service = EmbeddingsService()
        self.db_client = SupabaseClient()
        self.chat_service = ChatService()
        self.ui = UIComponents()
        
        # Initialize session state
        if "processed_docs" not in st.session_state:
            st.session_state.processed_docs = []
    
    def main_page(self):
        """Render the main application page"""
        # Render header
        self.ui.render_header()
        
        # Handle PDF upload
        uploaded_files = self.ui.render_pdf_uploader()
        
        # Process uploaded PDFs
        if uploaded_files:
            for pdf_file in uploaded_files:
                if pdf_file.name not in st.session_state.processed_docs:
                    status = self.ui.render_processing_status(f"Processing {pdf_file.name}...")
                    
                    try:
                        # Process PDF
                        chunks = self.pdf_processor.process_pdf(pdf_file, pdf_file.name)
                        status.info(f"Generating embeddings for {pdf_file.name}...")
                        
                        # Generate embeddings
                        chunks_with_embeddings = self.embedding_service.generate_batch_embeddings(chunks)
                        status.info(f"Storing document in the database...")
                        
                        # Store in database
                        self.db_client.store_document_chunks(chunks_with_embeddings)
                        
                        # Update processed documents list
                        st.session_state.processed_docs.append(pdf_file.name)
                        status.success(f"Successfully processed {pdf_file.name}")
                    except Exception as e:
                        status.error(f"Error processing {pdf_file.name}: {str(e)}")
        
        # Render document list in sidebar
        self.ui.render_document_list(st.session_state.processed_docs)
        
        # Show chat interface only if there are processed documents
        if st.session_state.processed_docs:
            query = self.ui.render_chat_interface()
            
            if query:
                # Add user query to chat history
                self.ui.add_message_to_history("user", query)
                
                try:
                    # Process query
                    response = self.chat_service.process_query(query)
                    
                    # Add response to chat history
                    self.ui.add_message_to_history("assistant", response["answer"])
                    
                    # Force a rerun to show the updated chat history
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.info("Upload and process PDF documents to start chatting")