from typing import List

from sqlmodel import Field, Relationship

from apps.core.models.base import BaseModel
from apps.core.models.blog import Blog


class Tag(BaseModel, table=True):
    __tablename__ = "tags"

    name: str = Field(max_length=255, index=True, unique=True, nullable=False)

    blogs: List["Blog"] = Relationship(back_populates="tags", link_model="BlogTag")
