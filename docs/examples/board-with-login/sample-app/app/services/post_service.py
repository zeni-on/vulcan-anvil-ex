from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models.post import Post
from app.repositories.post_repository import PostRepository


class PostService:
    def __init__(self, db: Session) -> None:
        self.posts = PostRepository(db)

    def list_posts(self) -> list[Post]:
        """REQ-003."""
        return self.posts.list_newest()

    def get_post(self, post_id: int) -> Post:
        """REQ-004."""
        post = self.posts.get_by_id(post_id)
        if post is None:
            raise AppError("ERR-005", 404)
        return post

    def create_post(self, title: str, content: str, author_id: int) -> Post:
        """REQ-005 / SEC-002 / SEC-004."""
        return self.posts.create(title=title, content=content, author_id=author_id)

    def update_post(self, post_id: int, title: str, content: str, current_user_id: int) -> Post:
        """REQ-006 / SEC-003."""
        post = self.get_post(post_id)
        if post.author_id != current_user_id:
            raise AppError("ERR-004", 403)
        return self.posts.update(post, title=title, content=content)

    def delete_post(self, post_id: int, current_user_id: int) -> None:
        """REQ-006 / SEC-003."""
        post = self.get_post(post_id)
        if post.author_id != current_user_id:
            raise AppError("ERR-004", 403)
        self.posts.delete(post)
