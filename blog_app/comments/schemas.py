from pydantic import BaseModel
from datetime import datetime


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    post_id: int


class CommentUpdate(CommentBase):
    """Schema for updating an existing comment."""
    pass


class CommentResponse(BaseModel):
    """Schema for returning a comment in response."""
    id: int
    user_id: int
    post_id: int
    content: str
    created_at: datetime

    class Config:
        orm_mode = True  # Enables automatic conversion of ORM objects to Pydantic models
