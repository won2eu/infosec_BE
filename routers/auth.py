from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from dependencies.db import get_db_session
from services.user_service import UserService
from models.schemas import UserCreate, UserLogin, UserResponse, Token
from models.user import Position

router = APIRouter(prefix="/auth", tags=["인증"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db_session)):
    """회원가입"""
    user_service = UserService(db)
    new_user = user_service.create_user(user_data)
    
    return UserResponse(
        id=new_user.id,
        login_id=new_user.login_id,
        name=new_user.name,
        position=Position(new_user.user_position),
        created_at=new_user.created_at.isoformat()
    )

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_db_session)):
    """로그인"""
    user_service = UserService(db)
    user = user_service.authenticate_user(login_data)
    access_token = user_service.create_access_token(user)
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    )
