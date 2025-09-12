from sqlmodel import Session, select
from passlib.context import CryptContext
from models.user import User
from models.schemas import UserCreate, UserLogin
from dependencies.jwt_utils import JWTUtil
from fastapi import HTTPException, status

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
jwt_util = JWTUtil()

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        """비밀번호를 해싱합니다."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호를 검증합니다."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, user_data: UserCreate) -> User:
        """새 사용자를 생성합니다."""
        # 중복된 login_id 확인
        existing_user = self.db.exec(select(User).where(User.login_id == user_data.login_id)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 로그인 ID입니다."
            )
        
        # 비밀번호 해싱
        hashed_password = self.hash_password(user_data.password)
        
        # 새 사용자 생성
        new_user = User(
            login_id=user_data.login_id,
            password=hashed_password,
            name=user_data.name,
            user_position=user_data.position.value
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        return new_user
    
    def authenticate_user(self, login_data: UserLogin) -> User:
        """사용자 인증을 수행합니다."""
        # 사용자 조회
        user = self.db.exec(select(User).where(User.login_id == login_data.login_id)).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="잘못된 로그인 ID 또는 비밀번호입니다."
            )
        
        # 비밀번호 검증
        if not self.verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="잘못된 로그인 ID 또는 비밀번호입니다."
            )
        
        return user
    
    def create_access_token(self, user: User) -> str:
        """사용자 정보로 JWT 토큰을 생성합니다."""
        payload = {
            "sub": str(user.id),
            "login_id": user.login_id,
            "name": user.name,
            "position": user.user_position
        }
        return jwt_util.create_token(payload)
