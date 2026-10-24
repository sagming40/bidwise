# 마이그레이션 테스트. "Alembic 마이그레이션을 끝까지 적용한 DB"와 "models.py"가 똑같은지 검사한다.
# models.py만 고치고 마이그레이션 파일을 안 만들면 여기서 실패한다.
# (임시 SQLite로 검사하므로 PostgreSQL 전용 차이는 못 잡는다. 그건 실제 DB에서 `alembic check`로 확인)

from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import inspect

from app.database import get_engine
from app.models import Base

BACKEND_DIR = Path(__file__).resolve().parent.parent


def alembic_config() -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return config


def test_마이그레이션_적용_결과가_모델과_같다():
    command.upgrade(alembic_config(), "head")

    with get_engine().connect() as connection:
        diff = compare_metadata(MigrationContext.configure(connection), Base.metadata)

    assert diff == []


def test_끝까지_되돌리면_테이블이_사라진다():
    config = alembic_config()
    command.upgrade(config, "head")
    command.downgrade(config, "base")

    tables = set(inspect(get_engine()).get_table_names())
    assert tables <= {"alembic_version"}
