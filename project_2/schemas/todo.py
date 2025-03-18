# # from pydantic import BaseModel, Field
# # from typing import Optional, List
# # from datetime import datetime

# # class TodoBase(BaseModel):
# #     title: str = Field(..., min_length=1, max_length=100)
# #     description: Optional[str] = None
# #     completed: Optional[bool] = False

# # class TodoCreate(TodoBase):
# #     pass

# # class TodoUpdate(BaseModel):
# #     title: Optional[str] = Field(None, min_length=1, max_length=100)
# #     description: Optional[str] = None
# #     completed: Optional[bool] = None

# # class TodoResponse(TodoBase):
# #     id: int
# #     deleted: bool = False
# #     deleted_at: Optional[datetime] = None
# #     created_at: datetime
# #     updated_at: Optional[datetime] = None  # Make updated_at optional

# #     class Config:
# #         from_attributes = True  # Change this line to enable from_orm

# # # New PaginatedResponse model
# # class PaginatedResponse(BaseModel):
# #     page: int
# #     limit: int
# #     total_items: int
# #     total_pages: int
# #     next: Optional[str]
# #     previous: Optional[str]
# #     data: List[TodoResponse]




# # from pydantic import BaseModel, Field
# # from typing import Optional
# # from datetime import datetime

# # class TodoBase(BaseModel):
# #     title: str = Field(..., min_length=1, max_length=100)
# #     description: Optional[str] = None
# #     completed: Optional[bool] = False

# # class TodoCreate(TodoBase):
# #     pass

# # class TodoUpdate(BaseModel):
# #     title: Optional[str] = Field(None, min_length=1, max_length=100)
# #     description: Optional[str] = None
# #     completed: Optional[bool] = None

# # class TodoResponse(TodoBase):
# #     id: int
# #     deleted: bool = False
# #     deleted_at: Optional[datetime] = None
# #     created_at: datetime
# #     updated_at: Optional[datetime] = None  # Make updated_at optional


# #     class Config:
# #         orm_mode = True


# # schemas/todo.py
# from pydantic import BaseModel, Field
# from typing import Optional, List, Any
# from datetime import datetime
# from bson import ObjectId

# class PyObjectId(ObjectId):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid ObjectId")
#         return ObjectId(v)

#     @classmethod
#     def __modify_schema__(cls, field_schema):
#         field_schema.update(type="string")

# class TodoBase(BaseModel):
#     title: str = Field(..., min_length=1, max_length=100)
#     description: Optional[str] = None
#     completed: Optional[bool] = False

# class TodoCreate(TodoBase):
#     pass

# class TodoUpdate(BaseModel):
#     title: Optional[str] = Field(None, min_length=1, max_length=100)
#     description: Optional[str] = None
#     completed: Optional[bool] = None

# class TodoResponse(TodoBase):
#     id: str
#     deleted: bool = False
#     deleted_at: Optional[datetime] = None
#     created_at: datetime
#     updated_at: Optional[datetime] = None

#     class Config:
#         populate_by_name = True
#         arbitrary_types_allowed = True
#         json_encoders = {ObjectId: str}
#         from_attributes = True

# # New PaginatedResponse model
# class PaginatedResponse(BaseModel):
#     current_page: int
#     total_pages: int
#     items_per_page: int
#     total_items: int
#     data: List[TodoResponse]

# schemas/todo.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TodoResponse(TodoBase):
    id: str
    created_at: datetime
    updated_at: datetime
    deleted: bool = False
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    current_page: int
    total_pages: int
    items_per_page: int
    total_items: int
    data: List[TodoResponse]
