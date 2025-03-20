
import streamlit as st
from src.ui.pages import AppPages
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    # Set page configuration
    st.set_page_config(
        page_title="PDF Chat App",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Print environment info for debugging
    import os
    from config.settings import OPENAI_API_KEY, SUPABASE_URL
    logger.info(f"OPENAI_API_KEY set: {'Yes' if OPENAI_API_KEY else 'No'}")
    logger.info(f"SUPABASE_URL set: {'Yes' if SUPABASE_URL else 'No'}")
    
    # Initialize app pages
    logger.info("Initializing application...")
    app = AppPages()
    
    # Render main page
    logger.info("Rendering main page...")
    app.main_page()

if __name__ == "__main__":
    main()


# import streamlit as st
# from src.ui.pages import AppPages

# def main():
#     """Main application entry point"""
#     # Set page configuration
#     st.set_page_config(
#         page_title="PDF Chat App",
#         page_icon="📚",
#         layout="wide",
#         initial_sidebar_state="expanded"
#     )
    
#     # Initialize app pages
#     app = AppPages()
    
#     # Render main page
#     app.main_page()

# if __name__ == "__main__":
#     main()