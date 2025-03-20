# PDF Chat Application

A Streamlit application that allows users to chat with their PDF documents using OpenAI embeddings and Supabase vector database.

## Features

- Upload multiple PDF documents
- Extract text from PDFs using PyPDF2
- Create embeddings using OpenAI
- Store document chunks and embeddings in Supabase
- Chat with your documents using natural language
- Similarity search to find relevant information

## Project Structure

The project follows a modular design with clear separation of concerns:

- `config/`: Configuration settings
- `src/`: Source code organized by functionality
  - `pdf/`: PDF processing logic
  - `embeddings/`: Embedding generation services
  - `database/`: Supabase client for vector storage
  - `chat/`: Chat interaction logic
  - `ui/`: Streamlit UI components
- `utils/`: Helper functions
- `data/`: Directory for storing data files

## Prerequisites

- Python 3.8+
- OpenAI API key
- Supabase account and project

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/pdf-chat-app.git
cd pdf-chat-app
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example` and add your API keys:
```
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Supabase Setup

1. Create a new Supabase project
2. Enable the Vector extension in SQL Editor:
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a table for storing document chunks
CREATE TABLE pdf_documents (
  id TEXT PRIMARY KEY,
  content TEXT,
  embedding VECTOR(1536),
  metadata JSONB
);

-- Create a function for similarity search
CREATE OR REPLACE FUNCTION match_documents (
  query_embedding VECTOR(1536),
  match_count INT DEFAULT 5
) RETURNS TABLE (
  id TEXT,
  content TEXT,
  metadata JSONB,
  similarity FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    pdf_documents.id,
    pdf_documents.content,
    pdf_documents.metadata,
    1 - (pdf_documents.embedding <=> query_embedding) as similarity
  FROM pdf_documents
  ORDER BY pdf_documents.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
```

## Usage

1. Run the application:
```
streamlit run app.py
```

2. Upload PDF documents
3. Ask questions about your documents in the chat interface

## License

MIT