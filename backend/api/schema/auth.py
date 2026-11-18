
from pydantic import BaseModel, Field, EmailStr


class RegisterRequest(BaseModel):
    full_name: str = Field(
        ...,
        title="Full Name",
        min_length=2,
        max_length=100,
        description="The full name of the user."
    )

    email: EmailStr

    password: str = Field(
        ...,
        title="Password",
        min_length=8,
        max_length=128,
        description="The password for the new user account."
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        title="Password",
        min_length=8,
        max_length=128,
        description="The password for the user account."
    )


class AuthResponse(BaseModel):
    message: str
    user_id: str | None = None
    full_name: str | None = None
    email: EmailStr | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"


class UserResponse(BaseModel):
    user_id: str
    full_name: str | None = None
    email: EmailStr | None = None
    authenticated: bool = True
