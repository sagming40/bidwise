# 이 파일의 역할 ─ "DB로 가는 길 관리"
# engine(연결선)과 Session(작업 단위)을 만드는 곳은 여기 한 군데뿐이다.
# Repository·API·스크립트는 전부 get_session()으로 세션을 받아 쓴다.

from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """
    engine은 연결을 재사용하는 풀(pool)을 품고 있어서, 프로그램 전체에서 하나만 만든다.
    pool_pre_ping=True: 꺼내 쓰기 전에 연결이 살아 있는지 한 번 확인한다.
    (PostgreSQL을 재시작했거나 오래 놀던 연결이 끊겼을 때, 에러 대신 새 연결을 잡는다)
    """
    return create_engine(get_settings().database_url, pool_pre_ping=True)


def get_session() -> Session:
    """
    세션 = 장바구니. 여러 저장 작업을 담았다가 commit()으로 한 번에 계산대를 통과시킨다.
    with 문과 함께 쓰면 끝날 때 자동으로 닫힌다.

        with get_session() as session:
            ...
            session.commit()
    """
    return Session(get_engine())
