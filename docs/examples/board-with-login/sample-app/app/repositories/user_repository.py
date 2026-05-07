from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def create(self, email: str, password_hash: str, user_nm: str) -> User:
        user = User(email=email, password_hash=password_hash, user_nm=user_nm)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
