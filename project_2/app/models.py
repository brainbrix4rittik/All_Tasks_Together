# # app/models.py
# from datetime import datetime
# from bson import ObjectId

# def create_todo_document(todo_data):
#     """Create a new todo document with required fields"""
#     now = datetime.now()
#     return {
#         "title": todo_data["title"],
#         "description": todo_data.get("description", ""),
#         "completed": todo_data.get("completed", False),
#         "deleted": False,
#         "deleted_at": None,
#         "created_at": now,
#         "updated_at": now
#     }

# def format_todo_response(todo):
#     """Format a todo document for response"""
#     if todo:
#         todo["id"] = str(todo["_id"])
#         del todo["_id"]
#     return todo

# app/models.py
from datetime import datetime
from bson import ObjectId
from typing import Dict, Any

def create_todo_document(todo_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new todo document with proper MongoDB formatting
    """
    # Add timestamps
    now = datetime.now()
    todo_document = {
        "title": todo_dict["title"],
        "description": todo_dict.get("description", ""),
        "completed": todo_dict.get("completed", False),
        "created_at": now,
        "updated_at": now,
        "deleted": False,
        "deleted_at": None
    }
    return todo_document

def format_todo_response(todo_document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a MongoDB document as a response
    """
    if not todo_document:
        return {}
    
    # Convert ObjectId to string
    todo_document["id"] = str(todo_document["_id"])
    
    # Remove the _id field
    todo_document.pop("_id", None)
    
    return todo_document
