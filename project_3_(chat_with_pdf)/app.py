import os
import gradio as gr
from dotenv import load_dotenv
from utils.pdf_utils import extract_text_from_pdf
from utils.openai_utils import get_llm_response

# Load environment variables from .env file
load_dotenv()

def chat_with_pdf(message, history, pdf_text):
    """Process a message within the chat interface"""
    if not pdf_text:
        return [], "Please upload a PDF document first."
    
    response = get_llm_response(message, pdf_text, history)
    history.append((message, response))
    return history, ""

def clear_and_upload(pdf_file):
    """Clear the chat history when a new PDF is uploaded"""
    if pdf_file is None:
        return None, "Please upload a PDF file."
    
    text = extract_text_from_pdf(pdf_file)
    return text, f"PDF uploaded and processed. Document length: {len(text)} characters. You can now ask questions about the content."

# Create the Gradio interface
with gr.Blocks(title="Chat with PDF using GPT-4o-mini") as demo:
    gr.Markdown("# Chat with your PDF Documents")
    gr.Markdown("Upload a PDF file and ask questions about its content.")
    
    with gr.Row():
        with gr.Column(scale=1):
            pdf_upload = gr.File(label="Upload PDF", file_types=[".pdf"])
            pdf_text = gr.State("")
            upload_message = gr.Textbox(label="Status", interactive=False)
            
            pdf_upload.upload(
                fn=clear_and_upload,
                inputs=[pdf_upload],
                outputs=[pdf_text, upload_message],
            )
        
    chatbot = gr.Chatbot(height=600)
    
    with gr.Row():
        message = gr.Textbox(
            label="Ask a question about your PDF",
            placeholder="What is this document about?",
            lines=2,
        )
        submit_button = gr.Button("Send", variant="primary")
    
    with gr.Row():
        clear_button = gr.Button("Clear Chat")
    
    # Handle interactions
    submit_button.click(
        fn=chat_with_pdf,
        inputs=[message, chatbot, pdf_text],
        outputs=[chatbot, message],
        queue=True,
    )
    
    message.submit(
        fn=chat_with_pdf,
        inputs=[message, chatbot, pdf_text],
        outputs=[chatbot, message],
        queue=True,
    )
    
    clear_button.click(lambda: [], None, chatbot, queue=False)

# Launch the app
if __name__ == "__main__":
    demo.launch(share=True)