from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.schemas.token import Token
from app.schemas.user import UserLogin, UserRegister, UserResponse
from app.services.auth_service import authenticate_user, register_user

auth_router = APIRouter()


@auth_router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user (student or admin)."""
    return register_user(db, data)


@auth_router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate and receive a JWT access token."""
    token = authenticate_user(db, data.email, data.password)
    return Token(access_token=token)


@auth_router.get("/me", response_model=UserResponse)
def get_profile(current_user=Depends(get_current_active_user)):
    """Get the authenticated user's profile."""
    return current_user