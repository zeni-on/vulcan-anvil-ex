from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.messages import get_message
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, SignupRequest, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/signup", status_code=201)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> dict:
    """REQ-001 / PGM-001 / SEC-001: signup."""
    user = AuthService(db).signup(payload.email, payload.password, payload.user_name)
    return {"data": UserResponse.from_model(user).model_dump(), "message": get_message("MSG-001")}


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict:
    """REQ-002 / PGM-002 / SEC-001: login."""
    token = AuthService(db).login(payload.email, payload.password)
    return {"data": LoginResponse(access_token=token).model_dump(), "message": get_message("MSG-001")}


@router.get("/me")
def me(current_user: User = Depends(get_current_user)) -> dict:
    """REQ-002 / SEC-002: return authenticated user summary."""
    return {"data": UserResponse.from_model(current_user).model_dump(), "message": get_message("MSG-001")}
