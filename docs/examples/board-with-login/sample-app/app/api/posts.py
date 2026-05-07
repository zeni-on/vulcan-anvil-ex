from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.messages import get_message
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.post import PostCreateRequest, PostResponse, PostUpdateRequest
from app.services.post_service import PostService

router = APIRouter()


@router.get("")
def list_posts(db: Session = Depends(get_db)) -> dict:
    """REQ-003 / PGM-003: list posts by newest first."""
    posts = PostService(db).list_posts()
    data = [PostResponse.from_model(post).model_dump() for post in posts]
    return {"data": data, "message": get_message("MSG-001")}


@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)) -> dict:
    """REQ-004 / PGM-004: get post detail."""
    post = PostService(db).get_post(post_id)
    return {"data": PostResponse.from_model(post).model_dump(), "message": get_message("MSG-001")}


@router.post("", status_code=201)
def create_post(
    payload: PostCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """REQ-005 / PGM-005 / SEC-002: create an authenticated post."""
    post = PostService(db).create_post(payload.title, payload.content, current_user.id)
    return {"data": PostResponse.from_model(post).model_dump(), "message": get_message("MSG-001")}


@router.put("/{post_id}")
def update_post(
    post_id: int,
    payload: PostUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """REQ-006 / PGM-006 / SEC-003: only the author can update a post."""
    post = PostService(db).update_post(post_id, payload.title, payload.content, current_user.id)
    return {"data": PostResponse.from_model(post).model_dump(), "message": get_message("MSG-001")}


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """REQ-006 / PGM-006 / SEC-003: only the author can delete a post."""
    PostService(db).delete_post(post_id, current_user.id)
    return {"data": {"deleted": True}, "message": get_message("MSG-001")}
