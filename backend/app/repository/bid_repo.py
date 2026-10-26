# 이 파일의 역할 ─ "창고 관리자"
# 하는 일: 정제된 행을 DB에 저장, 중복 처리, 낙찰결과를 공고에 연결, 재분류 결과 쓰기, 집계 쿼리
# 하지 않는 일: API 호출, 데이터 가공
# commit은 하지 않는다. 장바구니(session)를 언제 계산할지는 부르는 쪽이 정한다.

import logging
from datetime import date, datetime, time, timedelta

from sqlalchemy import case, func, select, tuple_, update
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.orm import Session

from app.models import BidAnnouncement, BidResult, utcnow

logger = logging.getLogger(__name__)

# 한 번에 보내는 행 수. PostgreSQL은 문장 하나에 파라미터를 65,535개까지 받는데,
# 공고 한 행이 13개를 쓰므로 1,000행(13,000개)이면 넉넉하다.
CHUNK_SIZE = 1000

ANNOUNCEMENT_KEY = ("bid_ntce_no", "bid_ntce_ord")
# 낙찰결과는 공고 하나에 하나뿐이라(1:0..1, UNIQUE) 어느 공고의 결과인지가 곧 신분증이다.
RESULT_KEY = ("announcement_id",)


def _insert(session: Session):
    """
    "있으면 고치고 없으면 넣기"(ON CONFLICT DO UPDATE)는 표준 SQL이 아니라 DB마다 문법이 다르다.
    실제 DB는 PostgreSQL, 테스트는 SQLite라서 연결된 DB에 맞는 insert를 고른다. (둘 다 쓰는 법은 같다)
    """
    dialect = session.get_bind().dialect.name
    return postgresql.insert if dialect == "postgresql" else sqlite.insert


def _upsert(session: Session, model, key: tuple[str, ...], rows: list[dict]) -> int:
    """
    key가 같은 행이 이미 있으면 나머지 컬럼과 fetched_at을 새 값으로 UPDATE, 없으면 INSERT.
    비유: 출석부에 이름을 적을 때, 이미 있는 이름이면 새 줄을 만들지 않고 그 줄의 메모만 고쳐 쓴다.

    반환값: 실제로 보낸 행 수 (중복을 걸러낸 뒤)
    """
    # 같은 키가 한 묶음 안에 두 번 들어 있으면 PostgreSQL이
    # "ON CONFLICT DO UPDATE command cannot affect row a second time"으로 묶음 전체를 거절한다.
    # 페이지를 넘기는 사이 목록이 밀리면 실제로 생길 수 있어서, 키가 같으면 나중 것만 남긴다.
    unique_rows = list({tuple(row[k] for k in key): row for row in rows}.values())
    if not unique_rows:
        return 0

    fetched_at = utcnow()
    insert = _insert(session)

    for start in range(0, len(unique_rows), CHUNK_SIZE):
        chunk = [{**row, "fetched_at": fetched_at} for row in unique_rows[start:start + CHUNK_SIZE]]
        stmt = insert(model).values(chunk)
        # excluded = "방금 넣으려다 부딪힌 새 값". 키를 뺀 나머지 컬럼을 그 값으로 덮어쓴다.
        update_columns = {col: stmt.excluded[col] for col in chunk[0] if col not in key}
        stmt = stmt.on_conflict_do_update(index_elements=list(key), set_=update_columns)
        session.execute(stmt)

    return len(unique_rows)


def upsert_announcements(session: Session, rows: list[dict]) -> int:
    """
    입찰공고를 (bid_ntce_no, bid_ntce_ord) 기준으로 UPSERT한다.
    이미 있는 공고는 id가 그대로라, 이미 붙어 있는 낙찰결과(announcement_id) 연결이 안 끊긴다.
    그래서 같은 기간을 두 번 수집해도 행 수가 늘지 않는다 (M1 완료 기준).
    """
    return _upsert(session, BidAnnouncement, ANNOUNCEMENT_KEY, rows)


def _announcement_ids(session: Session, keys: set[tuple[str, str]]) -> dict[tuple[str, str], int]:
    """(공고번호, 차수) → bid_announcements.id. DB에 없는 공고는 결과에 안 들어간다."""
    ids: dict[tuple[str, str], int] = {}
    keys = list(keys)
    for start in range(0, len(keys), CHUNK_SIZE):
        stmt = select(BidAnnouncement.bid_ntce_no, BidAnnouncement.bid_ntce_ord, BidAnnouncement.id).where(
            tuple_(BidAnnouncement.bid_ntce_no, BidAnnouncement.bid_ntce_ord).in_(keys[start:start + CHUNK_SIZE])
        )
        ids.update({(no, ord_): id_ for no, ord_, id_ in session.execute(stmt)})
    return ids


def upsert_results(session: Session, rows: list[dict]) -> tuple[int, int]:
    """
    낙찰결과를 해당 공고에 연결해서 UPSERT한다.
    - (bid_ntce_no, bid_ntce_ord)로 공고의 id를 찾아 announcement_id에 채운다 (두 API를 잇는 지점)
    - 공고가 DB에 없으면 건너뛴다. announcement_id는 NOT NULL이라 붙일 곳이 없다.
      공고를 먼저 수집하면(collect.py 순서) 같은 기간에서는 생기지 않고, 다음에 그 공고가 들어온 뒤 다시 수집하면 붙는다.

    반환값: (저장한 결과 수, 공고가 없어 건너뛴 수)
    """
    ids = _announcement_ids(session, {(row["bid_ntce_no"], row["bid_ntce_ord"]) for row in rows})

    linked = []
    skipped = 0
    for row in rows:
        announcement_id = ids.get((row["bid_ntce_no"], row["bid_ntce_ord"]))
        if announcement_id is None:
            skipped += 1
            continue
        linked.append({**row, "announcement_id": announcement_id})

    if skipped:
        logger.warning("공고가 DB에 없어 건너뛴 낙찰결과 %d건", skipped)

    return _upsert(session, BidResult, RESULT_KEY, linked), skipped


# ── M2: 재분류 ────────────────────────────────────────────────────────────

CLASSIFICATION_COLUMNS = ("region_normalized", "category", "category_source")


def get_classification_inputs(session: Session) -> list:
    """재분류에 필요한 원본 3개 + 지금 저장된 정제값 3개를 공고마다 꺼낸다."""
    stmt = select(
        BidAnnouncement.id,
        BidAnnouncement.cnstrtsite_rgn_nm,
        BidAnnouncement.main_cnstty_nm,
        BidAnnouncement.lcns_lmt_nm,
        BidAnnouncement.bid_ntce_nm,
        *(getattr(BidAnnouncement, col) for col in CLASSIFICATION_COLUMNS),
    )
    return list(session.execute(stmt))


def update_license_names(session: Session, licenses: dict[tuple[str, str], str]) -> int:
    """
    {(공고번호, 차수): 첫 면허 이름}으로 이미 저장된 공고의 lcns_lmt_nm만 채운다 (백필용).
    DB에 없는 공고의 면허는 무시한다. 반환값: 채운 공고 수
    """
    ids = _announcement_ids(session, set(licenses))
    rows = [{"id": id_, "lcns_lmt_nm": licenses[key]} for key, id_ in ids.items()]
    for start in range(0, len(rows), CHUNK_SIZE):
        session.execute(update(BidAnnouncement), rows[start:start + CHUNK_SIZE])
    return len(rows)


def update_classifications(session: Session, rows: list[dict]) -> int:
    """
    {"id": .., "region_normalized": .., "category": .., "category_source": ..} 목록으로 정제 컬럼만 고친다.
    기본키(id)가 들어 있는 dict 목록을 update()에 넘기면 SQLAlchemy가 행마다 UPDATE ... WHERE id=? 를 묶어서 보낸다.
    """
    for start in range(0, len(rows), CHUNK_SIZE):
        session.execute(update(BidAnnouncement), rows[start:start + CHUNK_SIZE])
    return len(rows)


# ── M2: 집계 쿼리 ──────────────────────────────────────────────────────────
# 전부 공고 기준 LEFT JOIN이다. INNER JOIN이면 결과가 없는(개찰 전·유찰) 공고가 통계에서 사라진다.
#   COUNT(*)          = 전체 공고
#   COUNT(r.id)       = 결과가 붙은 공고 (NULL은 안 센다)
#   AVG(r.sucsfbid_rate) = 결과가 있고 낙찰률이 있는 것만으로 낸 평균 (NULL은 알아서 빠진다)

UNCLASSIFIED = "미분류"


def _period_filter(date_from: date, date_to: date):
    """
    bid_ntce_dt가 date_from 0시 이상, date_to 다음 날 0시 미만.
    BETWEEN으로 date_to를 넣으면 그날 0시까지만 잡혀서 마지막 날 공고가 빠진다.
    """
    start = datetime.combine(date_from, time.min)
    end = datetime.combine(date_to + timedelta(days=1), time.min)
    return (BidAnnouncement.bid_ntce_dt >= start) & (BidAnnouncement.bid_ntce_dt < end)


def _base_counts():
    return (
        func.count().label("total_count"),
        func.count(BidResult.id).label("completed_count"),
        func.avg(BidResult.sucsfbid_rate).label("avg_sucsfbid_rate"),
    )


def get_summary(session: Session, date_from: date, date_to: date, region: str | None = None) -> dict:
    """대시보드 요약 카드 (04_api_spec.md 3.1절)."""
    stmt = (
        select(*_base_counts(), func.coalesce(func.sum(BidAnnouncement.bdgt_amt), 0).label("total_budget_amt"))
        .select_from(BidAnnouncement)
        .outerjoin(BidResult, BidResult.announcement_id == BidAnnouncement.id)
        .where(_period_filter(date_from, date_to))
    )
    if region:
        stmt = stmt.where(BidAnnouncement.region_normalized == region)
    row = session.execute(stmt).one()
    return {
        "total_announcements": row.total_count,
        "completed_count": row.completed_count,
        "pending_count": row.total_count - row.completed_count,
        "avg_sucsfbid_rate": row.avg_sucsfbid_rate,
        # PostgreSQL의 SUM(BIGINT)는 numeric(Decimal)으로 돌아온다 (SQLite는 int라 테스트로는 안 보였다 ─ 2026-10-26 실제 DB에서 발견).
        # 금액 합계는 원 단위 정수라 int로 맞춘다 (04_api_spec.md 3.1절)
        "total_budget_amt": int(row.total_budget_amt),
    }


def get_region_stats(session: Session, date_from: date, date_to: date) -> list[dict]:
    """지역별 낙찰률 (지도용, 04_api_spec.md 3.2절). 결과가 하나도 없는 지역도 avg=None으로 포함된다."""
    stmt = (
        select(
            BidAnnouncement.region_normalized.label("region"),
            *_base_counts(),
            func.avg(BidAnnouncement.bdgt_amt).label("avg_budget_amt"),
        )
        .select_from(BidAnnouncement)
        .outerjoin(BidResult, BidResult.announcement_id == BidAnnouncement.id)
        .where(_period_filter(date_from, date_to))
        .group_by(BidAnnouncement.region_normalized)
        .order_by(func.count().desc())
    )
    return [row._asdict() for row in session.execute(stmt)]


def get_category_stats(
    session: Session, date_from: date, date_to: date, region: str | None = None, limit: int = 10
) -> list[dict]:
    """
    공종 대분류별 낙찰률 (막대차트용, 04_api_spec.md 3.3절). 분류 못한 공고는 "미분류"로 묶는다.
    한 대분류 안에 업종으로 분류된 것과 키워드로 추정한 것이 섞이므로, 추정 건수(keyword_count)를 같이 준다.
    """
    category = func.coalesce(BidAnnouncement.category, UNCLASSIFIED).label("category")
    stmt = (
        select(
            category,
            *_base_counts(),
            func.sum(case((BidAnnouncement.category_source == "keyword", 1), else_=0)).label("keyword_count"),
        )
        .select_from(BidAnnouncement)
        .outerjoin(BidResult, BidResult.announcement_id == BidAnnouncement.id)
        .where(_period_filter(date_from, date_to))
        .group_by(category)
        .order_by(func.count().desc())
        .limit(limit)
    )
    if region:
        stmt = stmt.where(BidAnnouncement.region_normalized == region)
    return [row._asdict() for row in session.execute(stmt)]
