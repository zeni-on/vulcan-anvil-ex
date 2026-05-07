from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.post import Post


class PostRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_newest(self) -> list[Post]:
        return list(self.db.scalars(select(Post).order_by(Post.created_at.desc(), Post.id.desc())))

    def get_by_id(self, post_id: int) -> Post | None:
        return self.db.get(Post, post_id)

    def create(self, title: str, content: str, author_id: int) -> Post:
        post = Post(post_ttl=title, post_cn=content, author_id=author_id)
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def update(self, post: Post, title: str, content: str) -> Post:
        post.post_ttl = title
        post.post_cn = content
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete(self, post: Post) -> None:
        self.db.delete(post)
        self.db.commit()
