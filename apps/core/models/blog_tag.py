import uuid

from sqlmodel import SQLModel, Field


class BlogTag(SQLModel, table=True):
    __tablename__ = "blog_tags"

    blog_id: uuid.UUID = Field(foreign_key="blogs.id", primary_key=True, nullable=False)
    tag_id: uuid.UUID = Field(foreign_key="tags.id", primary_key=True, nullable=False)
