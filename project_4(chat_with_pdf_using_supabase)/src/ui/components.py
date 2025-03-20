import streamlit as st

class UIComponents:
    """
    Class containing UI components for the Streamlit application
    """
    
    @staticmethod
    def render_header():
        """Render the application header"""
        st.title("PDF Chat Application")
        st.write("Upload PDF documents and chat with them using AI")
    
    @staticmethod
    def render_pdf_uploader():
        """
        Render the PDF file uploader
        
        Returns:
            uploaded_files: List of uploaded PDF files
        """
        st.subheader("Upload PDF Documents")
        uploaded_files = st.file_uploader(
            "Choose PDF files", 
            type="pdf", 
            accept_multiple_files=True
        )
        return uploaded_files
    
    @staticmethod
    def render_processing_status(status_text):
        """Render the processing status"""
        status_container = st.empty()
        status_container.info(status_text)
        return status_container
    
    @staticmethod
    def render_chat_interface():
        """
        Render the chat interface
        
        Returns:
            query: User query from chat input
        """
        st.subheader("Chat with your Documents")
        
        # Initialize chat history if it doesn't exist
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**AI:** {message['content']}")
        
        # Chat input
        query = st.chat_input("Ask something about your documents")
        
        return query
    
    @staticmethod
    def add_message_to_history(role, content):
        """
        Add a message to the chat history
        
        Args:
            role: Role of the message sender (user/assistant)
            content: Content of the message
        """
        st.session_state.chat_history.append({
            "role": role,
            "content": content
        })
    
    @staticmethod
    def render_document_list(document_names):
        """
        Render the list of processed documents
        
        Args:
            document_names: List of document names
        """
        if document_names:
            st.sidebar.subheader("Processed Documents")
            for doc in document_names:
                st.sidebar.text(f"• {doc}")