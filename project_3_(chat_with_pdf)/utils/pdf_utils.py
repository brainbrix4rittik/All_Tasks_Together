import PyPDF2

def extract_text_from_pdf(pdf_file):
    """Extract text from an uploaded PDF file"""
    if pdf_file is None:
        return "Please upload a PDF file."
    
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def summarize_text(text, max_tokens=4000):
    """Truncate text to fit within token limits"""
    # Simple truncation - in a production app, you'd use a more sophisticated approach
    # This is a very basic approximation assuming avg 4 chars per token
    max_chars = max_tokens * 4
    if len(text) > max_chars:
        return text[:max_chars] + "... [truncated]"
    return text