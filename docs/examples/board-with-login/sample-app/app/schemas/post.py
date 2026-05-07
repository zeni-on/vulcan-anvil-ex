from datetime import datetime

from pydantic import BaseModel, Field

from app.models.post import Post


class PostCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=4000)


class PostUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=4000)


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, post: Post) -> "PostResponse":
        return cls(
            id=post.id,
            title=post.post_ttl,
            content=post.post_cn,
            author_id=post.author_id,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
