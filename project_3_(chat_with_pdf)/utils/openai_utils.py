import os
from dotenv import load_dotenv
import openai
from .pdf_utils import summarize_text

# Set your OpenAI API key
openai.api_key= "YOUR_API_KEY"

def get_llm_response(prompt, pdf_text, history):
    """Get response from OpenAI's GPT-4o-mini model"""
    if not pdf_text:
        return "Please upload a PDF document first."
    
    # Prepare conversation history for the API
    messages = [
        {"role": "system", "content": f"You are a helpful assistant that answers questions based on the following document content. Document content: {summarize_text(pdf_text)}"}
    ]
    
    # Add conversation history - history is a list of (user, assistant) message tuples
    for user_msg, ai_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": ai_msg})
    
    # Add the current question
    messages.append({"role": "user", "content": prompt})
    
    try:
        # Make the API call to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"