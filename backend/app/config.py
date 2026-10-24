# 이 파일의 역할 ─ "금고 관리자"
# .env(금고)를 여는 곳은 여기 한 군데뿐이다. 다른 파일은 get_settings()로 열쇠를 받아 간다.
# 예전엔 파일마다 load_dotenv()를 부르고 키가 있는지 직접 검사했는데,
# 파일이 늘수록 같은 코드가 복사되고, import만 해도 예외가 나서 테스트를 쓰기 어려웠다.

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ 폴더. 어느 위치에서 실행하든 backend/.env를 찾도록 경로를 고정한다.
BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    .env에 있어야 하는 값 목록. 필드 이름은 대소문자 구분 없이 환경변수와 짝지어진다
    (database_url ↔ DATABASE_URL).
    값이 없으면 get_settings()를 부르는 순간 ValidationError로 "무엇이 빠졌는지" 알려준다.
    """

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str

    # ⚠️ URL 인코딩되지 않은 원본 키(% 없음)여야 한다.
    # requests의 params가 자동으로 인코딩하므로, 인코딩된 키를 넣으면 이중 인코딩되어 인증에 실패한다.
    data_go_kr_service_key: str


@lru_cache
def get_settings() -> Settings:
    """
    처음 부를 때 한 번만 .env를 읽고, 이후엔 같은 객체를 돌려준다.
    import 시점이 아니라 "실제로 필요할 때" 읽기 때문에, 테스트에서는 환경변수로 값을 바꿔 끼울 수 있다.
    (환경변수가 .env보다 우선한다)
    """
    return Settings()
