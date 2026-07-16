from datetime import datetime

from pydantic import Field

from app.schemas.common import CamelModel, PaginationMeta


class PostCreate(CamelModel):
    type: str = "GENERAL"
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    nickname: str = Field(default="익명", max_length=50)
    password: str = Field(min_length=1, max_length=100)
    tags: list[str] = []


class PostUpdate(CamelModel):
    password: str
    type: str | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    nickname: str | None = Field(default=None, max_length=50)
    tags: list[str] | None = None


class PasswordRequest(CamelModel):
    password: str


class LikeRequest(CamelModel):
    client_id: str = Field(min_length=1, max_length=100)


class LikeResponse(CamelModel):
    liked: bool
    likes_count: int


class PostOut(CamelModel):
    id: int
    type: str
    title: str
    content: str
    nickname: str
    tags: list[str]
    views: int
    likes: int
    comment_count: int
    created_at: datetime
    updated_at: datetime


class PostListResponse(CamelModel):
    items: list[PostOut]
    meta: PaginationMeta


class CommentCreate(CamelModel):
    content: str = Field(min_length=1)
    nickname: str = Field(default="익명", max_length=50)
    password: str = Field(min_length=1, max_length=100)


class CommentUpdate(CamelModel):
    password: str
    content: str = Field(min_length=1)
    nickname: str | None = Field(default=None, max_length=50)


class CommentOut(CamelModel):
    id: int
    post_id: int
    content: str
    nickname: str
    created_at: datetime
    updated_at: datetime
