# dependencies/redis_client.py
import redis
import os
from dotenv import load_dotenv
import json
from typing import Optional, Dict, Any

load_dotenv()

# Redis 연결 설정
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

class RedisSessionManager:
    def __init__(self):
        self.redis = redis_client
    
    def create_session(self, user_id: str, token: str, ttl: int = 1800) -> bool:
        """사용자 세션을 Redis에 저장합니다. (기본 30분 TTL)"""
        try:
            session_data = {
                "user_id": user_id,
                "token": token,
                "active": True
            }
            self.redis.setex(f"session:{user_id}", ttl, json.dumps(session_data))
            return True
        except Exception as e:
            print(f"Redis 세션 생성 오류: {e}")
            return False
    
    def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 세션 정보를 가져옵니다."""
        try:
            session_data = self.redis.get(f"session:{user_id}")
            if session_data:
                return json.loads(session_data)
            return None
        except Exception as e:
            print(f"Redis 세션 조회 오류: {e}")
            return None
    
    def delete_session(self, user_id: str) -> bool:
        """사용자 세션을 삭제합니다 (로그아웃)."""
        try:
            self.redis.delete(f"session:{user_id}")
            return True
        except Exception as e:
            print(f"Redis 세션 삭제 오류: {e}")
            return False
    
    def is_session_active(self, user_id: str) -> bool:
        """사용자 세션이 활성화되어 있는지 확인합니다."""
        session = self.get_session(user_id)
        return session is not None and session.get("active", False)
    
    def extend_session(self, user_id: str, ttl: int = 1800) -> bool:
        """세션 TTL을 연장합니다."""
        try:
            return self.redis.expire(f"session:{user_id}", ttl)
        except Exception as e:
            print(f"Redis 세션 연장 오류: {e}")
            return False

# 전역 세션 매니저 인스턴스
session_manager = RedisSessionManager()
