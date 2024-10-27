import uuid

from sqlmodel import Relationship, Field

from apps.core.models.base import BaseModel
from apps.core.models.blog import Blog
from apps.core.models.user import User


class Comment(BaseModel, table=True):
    __tablename__ = "comments"

    content: str
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    blog_id: uuid.UUID = Field(foreign_key="blogs.id", nullable=False)

    user: User = Relationship(back_populates="comments")
    blog: Blog = Relationship(back_populates="comments")
