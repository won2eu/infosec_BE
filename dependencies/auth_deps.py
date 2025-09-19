# dependencies/auth_deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dependencies.jwt_utils import JWTUtil
from dependencies.redis_client import session_manager
from typing import Tuple

security = HTTPBearer()
jwt_util = JWTUtil()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """현재 인증된 사용자 정보를 반환합니다."""
    token = credentials.credentials
    payload = jwt_util.decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Redis에서 세션 확인
    user_id = payload.get("sub")
    if not session_manager.is_session_active(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="세션이 만료되었거나 로그아웃되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

async def get_current_user_with_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Tuple[dict, str]:
    """현재 인증된 사용자 정보와 토큰을 함께 반환합니다."""
    token = credentials.credentials
    payload = jwt_util.decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Redis에서 세션 확인
    user_id = payload.get("sub")
    if not session_manager.is_session_active(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="세션이 만료되었거나 로그아웃되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload, token
