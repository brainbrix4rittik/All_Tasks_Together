import os
import PyPDF2
from typing import List, Dict, Any, Generator
import uuid
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

class PDFProcessor:
    """
    Class responsible for processing PDF files, extracting text and chunking.
    """
    
    @staticmethod
    def extract_text_from_pdf(pdf_file) -> str:
        """
        Extract text from a PDF file using PyPDF2
        
        Args:
            pdf_file: File object of the uploaded PDF
            
        Returns:
            str: Extracted text from the PDF
        """
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
                
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    @staticmethod
    def create_chunks(text: str) -> List[Dict[str, Any]]:
        """
        Split text into chunks with specified size and overlap
        
        Args:
            text: Full text to be chunked
            
        Returns:
            List[Dict]: List of chunks with metadata
        """
        if not text:
            return []
            
        chunks = []
        
        # Generate overlapping chunks of text
        for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP):
            chunk_text = text[i:i + CHUNK_SIZE]
            
            if len(chunk_text.strip()) > 0:
                chunk_id = str(uuid.uuid4())
                chunks.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "metadata": {
                        "chunk_index": len(chunks),
                        "char_start": i,
                        "char_end": i + len(chunk_text)
                    }
                })
                
        return chunks
    
    @staticmethod
    def process_pdf(pdf_file, filename: str) -> List[Dict[str, Any]]:
        """
        Process a PDF file by extracting text and creating chunks
        
        Args:
            pdf_file: File object of the uploaded PDF
            filename: Name of the PDF file
            
        Returns:
            List[Dict]: List of chunks with metadata
        """
        text = PDFProcessor.extract_text_from_pdf(pdf_file)
        chunks = PDFProcessor.create_chunks(text)
        
        # Add file metadata to each chunk
        for chunk in chunks:
            chunk["metadata"]["filename"] = filename
            chunk["metadata"]["source"] = filename
            
        return chunks