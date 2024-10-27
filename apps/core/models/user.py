from datetime import datetime
from typing import List

from passlib.context import CryptContext
from sqlmodel import Field, Relationship, Column, DateTime

from apps.core.models.base import BaseModel
from apps.core.models.blog import Blog
from apps.core.models.comment import Comment

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel, table=True):
    __tablename__ = "users"

    email: str = Field(max_length=255, index=True, unique=True, nullable=False)
    password: str

    blogs: List["Blog"] = Relationship(back_populates="user")
    comments: List["Comment"] = Relationship(back_populates="user")

    last_login_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=True))

    @staticmethod
    def hash_password(plain_password: str) -> str:
        return pwd_context.hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password)
