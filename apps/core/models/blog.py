import uuid
from typing import List

from sqlmodel import Field, Relationship

from apps.core.models.base import BaseModel
from apps.core.models.comment import Comment
from apps.core.models.tag import Tag
from apps.core.models.user import User


class Blog(BaseModel, table=True):
    __tablename__ = "blogs"

    title: str = Field(max_length=255, index=True, nullable=False)
    content: str
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)

    user: User = Relationship(back_populates="blogs")

    comments: List["Comment"] = Relationship(back_populates="blog")
    tags: List["Tag"] = Relationship(back_populates="blogs", link_model="BlogTag")
