# 0005 · 스키마는 Alembic으로, 패키지는 버전 고정으로 기기끼리 맞춘다

- **상태**: 채택
- **날짜**: 2026-10-24 (2026-11-04 소급 기록)

## 맥락

기기 3대(노트북 · 집 데스크탑 · 회사 PC)에서 작업하고 DB는 기기마다 따로다. M2에서 컬럼을 더해야 하는데 수동 `ALTER TABLE`로 맞추면 틀리기 쉽다.
`requirements.txt`에 버전이 없어서 새 venv에 SQLAlchemy 2.1이 깔렸고, 기본 드라이버가 psycopg 3으로 바뀌어 `ModuleNotFoundError: No module named 'psycopg'`로 접속부터 실패했다.

## 결정

- 스키마 변경은 Alembic 마이그레이션으로만 한다. `git pull` 뒤 `alembic upgrade head`. `create_tables.py`는 지웠다.
- 모든 패키지를 `==`로 고정한다. 드라이버는 psycopg 3.
- `pytest`의 마이그레이션 테스트가 "끝까지 적용한 결과 == `models.py`"를 확인한다.

운영 규칙(번호 붙이기, 만드는 기기, `stamp`)은 `CLAUDE.md` "기기 3대"가 원본이다.

## 검토한 대안

- **`create_all` + 수동 `ALTER TABLE`** — 기기마다 어긋나도 알 수 없다.

## 감수할 것

- 테스트는 SQLite라 PostgreSQL과 반환 타입이 다를 수 있다(`SUM(BIGINT)`가 `Decimal`). 실제 DB 확인을 한 번 더 한다.
- 버전을 올릴 때마다 다른 기기에서 다시 설치해야 한다.
