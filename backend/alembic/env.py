# Alembic이 마이그레이션을 실행할 때 처음 읽는 파일.
# 역할은 두 가지: (1) 어느 DB에 적용할지 (2) "있어야 할 모습"(models.py)이 무엇인지 알려주기.

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.config import get_settings
from app.models import Base

config = context.config

# alembic.ini의 [loggers] 설정 적용. disable_existing_loggers=False:
# 앱이나 pytest가 미리 만들어 둔 로거를 꺼버리지 않도록 한다.
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# autogenerate가 비교할 기준 = models.py에 선언한 테이블들
target_metadata = Base.metadata

# DB 주소는 alembic.ini가 아니라 .env에서 가져온다 (app/config.py 한 곳에서만 읽는다).
# alembic.ini에 적으면 비밀번호가 git에 올라가고, 기기마다 다른 값을 담을 수도 없다.
database_url = get_settings().database_url


def run_migrations_offline() -> None:
    """DB에 접속하지 않고 실행할 SQL만 출력한다. (alembic upgrade head --sql)"""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """DB에 접속해서 실제로 적용한다."""
    connectable = create_engine(database_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite(테스트용)는 ALTER TABLE이 약해서, 테이블을 새로 만들어 옮기는 batch 방식이 필요하다.
            render_as_batch=connection.dialect.name == "sqlite",
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
