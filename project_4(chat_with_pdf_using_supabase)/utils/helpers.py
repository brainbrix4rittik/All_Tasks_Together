import os
import json
from typing import Dict, Any, List

def ensure_directory_exists(directory: str) -> None:
    """
    Ensure that a directory exists, create it if it doesn't
    
    Args:
        directory: Path to the directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_json(data: Dict[str, Any], filepath: str) -> None:
    """
    Save data as JSON to a file
    
    Args:
        data: Data to be saved
        filepath: Path to save the file
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load JSON data from a file
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Dict: Loaded JSON data
    """
    with open(filepath, 'r') as f:
        return json.load(f)

def truncate_text(text: str, max_length: int) -> str:
    """
    Truncate text to a maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def format_sources(sources: List[Dict[str, Any]]) -> str:
    """
    Format source information for display
    
    Args:
        sources: List of source documents
        
    Returns:
        str: Formatted source information
    """
    formatted_sources = []
    
    for i, source in enumerate(sources, 1):
        filename = source.get("metadata", {}).get("filename", "Unknown")
        formatted_sources.append(f"{i}. {filename}")
    
    return "\n".join(formatted_sources)