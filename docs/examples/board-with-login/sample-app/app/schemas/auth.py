from pydantic import BaseModel, EmailStr, Field

from app.models.user import User


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    user_name: str = Field(min_length=1, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class UserResponse(BaseModel):
    id: int
    email: str
    user_name: str

    @classmethod
    def from_model(cls, user: User) -> "UserResponse":
        return cls(id=user.id, email=user.email, user_name=user.user_nm)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
