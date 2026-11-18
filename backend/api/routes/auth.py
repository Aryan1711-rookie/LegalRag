
from fastapi import APIRouter, HTTPException, status, Depends
from supabase_auth.errors import AuthApiError

from database.supabase import create_auth_client
from api.dependencies.auth import get_current_user
from api.schema.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    UserResponse
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(payload: RegisterRequest):
    supabase = create_auth_client()

    try:
        response = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password,
            "options": {
                "data": {
                    "full_name": payload.full_name.strip()
                }
            }
        })

        user = response.user
        session = response.session

        return AuthResponse(
            message=(
                "Registration successful. Please check your email to confirm your account."
                if session is None else "Registration successful."
            ),
            user_id=str(user.id) if user else None,
            full_name=payload.full_name.strip(),
            email=user.email if user else None,
            access_token=session.access_token if session else None,
            refresh_token=session.refresh_token if session else None
        )

    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {e.message}"
        )


@router.post("/login", response_model=AuthResponse)
def login_user(payload: LoginRequest):
    supabase = create_auth_client()

    try:
        response = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password
        })

        user = response.user
        session = response.session

        if not user or not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        user_metadata = user.user_metadata or {}

        return AuthResponse(
            message="Login successful.",
            user_id=str(user.id),
            full_name=user_metadata.get("full_name"),
            email=user.email,
            access_token=session.access_token,
            refresh_token=session.refresh_token
        )

    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Login failed: {e.message}"
        )


@router.get("/me", response_model=UserResponse)
def get_my_profile(user=Depends(get_current_user)):
    user_metadata = user.user_metadata or {}

    return UserResponse(
        user_id=str(user.id),
        full_name=user_metadata.get("full_name"),
        email=user.email,
        authenticated=True
    )
