import json
from pathlib import Path

import pytest

from app.config import get_settings
from app.database import get_engine, get_session
from app.models import Base

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def test_settings(monkeypatch, tmp_path):
    """
    테스트는 실제 .env(진짜 DB·인증키)를 쓰지 않는다.
    환경변수가 .env보다 우선하므로, 여기서 가짜 값을 끼워 넣고 설정 캐시를 비운다.
    DB는 테스트마다 새로 만드는 임시 SQLite 파일이다.
    """
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("DATA_GO_KR_SERVICE_KEY", "test-key")
    get_settings.cache_clear()
    get_engine.cache_clear()
    yield
    get_settings.cache_clear()
    get_engine.cache_clear()


@pytest.fixture
def announcements_page() -> dict:
    """
    입찰공고 API 응답 1페이지.
    ⚠️ 실제 응답의 뼈대(header/body/items/totalCount)를 본뜬 예시다. 공고번호·공고명은 2026-09-13 실측값이지만
    나머지 필드 값은 지어낸 것. 다음에 실제 API를 호출할 때 응답 원문을 저장해서 바꿔 넣는다.
    """
    return json.loads((FIXTURES_DIR / "announcements_page.json").read_text(encoding="utf-8"))


@pytest.fixture
def real_announcements_page() -> dict:
    """
    입찰공고 API 실제 응답 원문 (2026-10-20 공고분, 10건 중 3건만 남김. 필드 143개 그대로).
    변환 코드가 "진짜 모양"의 데이터에서 깨지지 않는지 확인하는 용도.
    """
    return json.loads((FIXTURES_DIR / "announcements_real.json").read_text(encoding="utf-8"))


@pytest.fixture
def real_results_page() -> dict:
    """
    낙찰정보 API 실제 응답 원문 (2026-10-20 공고분, 72건 중 3건: 보통 / 정수 낙찰률 "90" / 빈 낙찰률 "").
    쓰지 않는 개인정보성 필드(대표자명·주소·전화·사업자번호·담당자)는 비워서 저장했다.
    """
    return json.loads((FIXTURES_DIR / "results_real.json").read_text(encoding="utf-8"))


@pytest.fixture
def session():
    """
    테이블을 만들어 둔 임시 SQLite 세션. 테이블 구조는 마이그레이션 테스트가 models.py와 같다는 걸 보장하므로
    여기서는 create_all로 빠르게 만든다.
    """
    Base.metadata.create_all(get_engine())
    with get_session() as session:
        yield session
