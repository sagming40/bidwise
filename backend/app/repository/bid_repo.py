# 이 파일의 역할 ─ "창고 관리자"
# 하는 일: 정제된 행을 DB에 저장, 중복 처리 (나중엔 집계 쿼리도 여기에)
# 하지 않는 일: API 호출, 데이터 가공
# commit은 하지 않는다. 장바구니(session)를 언제 계산할지는 부르는 쪽이 정한다.

from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.orm import Session

from app.models import BidAnnouncement, utcnow

# 한 번에 보내는 행 수. PostgreSQL은 문장 하나에 파라미터를 65,535개까지 받는데,
# 공고 한 행이 13개를 쓰므로 1,000행(13,000개)이면 넉넉하다.
CHUNK_SIZE = 1000

ANNOUNCEMENT_KEY = ("bid_ntce_no", "bid_ntce_ord")


def _insert(session: Session):
    """
    "있으면 고치고 없으면 넣기"(ON CONFLICT DO UPDATE)는 표준 SQL이 아니라 DB마다 문법이 다르다.
    실제 DB는 PostgreSQL, 테스트는 SQLite라서 연결된 DB에 맞는 insert를 고른다. (둘 다 쓰는 법은 같다)
    """
    dialect = session.get_bind().dialect.name
    return postgresql.insert if dialect == "postgresql" else sqlite.insert


def upsert_announcements(session: Session, rows: list[dict]) -> int:
    """
    입찰공고를 (bid_ntce_no, bid_ntce_ord) 기준으로 UPSERT한다.
    - 처음 보는 공고 → INSERT
    - 이미 있는 공고 → 나머지 컬럼과 fetched_at을 최신 값으로 UPDATE (id는 그대로라 낙찰결과 연결이 안 끊긴다)
    그래서 같은 기간을 두 번 수집해도 행 수가 늘지 않는다 (M1 완료 기준).

    비유: 출석부에 이름을 적을 때, 이미 있는 이름이면 새 줄을 만들지 않고 그 줄의 메모만 고쳐 쓴다.

    반환값: 실제로 보낸 공고 수 (중복을 걸러낸 뒤)
    """
    # 같은 공고가 한 묶음 안에 두 번 들어 있으면 PostgreSQL이
    # "ON CONFLICT DO UPDATE command cannot affect row a second time"으로 묶음 전체를 거절한다.
    # 페이지를 넘기는 사이 목록이 밀리면 실제로 생길 수 있어서, 키가 같으면 나중 것만 남긴다.
    unique_rows = list({tuple(row[k] for k in ANNOUNCEMENT_KEY): row for row in rows}.values())
    if not unique_rows:
        return 0

    fetched_at = utcnow()
    insert = _insert(session)

    for start in range(0, len(unique_rows), CHUNK_SIZE):
        chunk = [{**row, "fetched_at": fetched_at} for row in unique_rows[start:start + CHUNK_SIZE]]
        stmt = insert(BidAnnouncement).values(chunk)
        # excluded = "방금 넣으려다 부딪힌 새 값". 키를 뺀 나머지 컬럼을 그 값으로 덮어쓴다.
        update_columns = {col: stmt.excluded[col] for col in chunk[0] if col not in ANNOUNCEMENT_KEY}
        stmt = stmt.on_conflict_do_update(index_elements=list(ANNOUNCEMENT_KEY), set_=update_columns)
        session.execute(stmt)

    return len(unique_rows)
