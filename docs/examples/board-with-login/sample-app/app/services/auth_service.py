from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)

    def signup(self, email: str, password: str, user_name: str) -> User:
        """REQ-001 / SEC-001 / SEC-004."""
        if self.users.get_by_email(email) is not None:
            raise AppError("ERR-001", 409)
        return self.users.create(email=email, password_hash=hash_password(password), user_nm=user_name)

    def login(self, email: str, password: str) -> str:
        """REQ-002 / SEC-001."""
        user = self.users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise AppError("ERR-002", 401)
        return create_access_token(user.id)
