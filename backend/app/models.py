from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import BigInteger, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    """
    수집 시각(fetched_at)용 현재 시각. UTC 기준이고, 컬럼이 timestamp(시간대 없음)라서 시간대 정보는 떼고 저장한다.
    datetime.utcnow()는 Python 3.12부터 deprecated라 이렇게 바꿨다.
    ⚠️ 시간대가 붙은 값을 그대로 넣으면 PostgreSQL이 세션 시간대(한국)로 바꿔 저장해서 9시간 어긋난다.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


# Base = "이 아래에 있는 클래스들은 전부 진짜 테이블이다"라는 표지판
# SQLAlchemy와 Alembic이 이 표지판이 붙은 class들을 한데 모아 테이블 구조를 파악한다.
class Base(DeclarativeBase):
    pass


# SQLAlchemy 2.0 스타일 읽는 법:
#   Mapped[str]        → NOT NULL (값이 반드시 있음)
#   Mapped[str | None] → NULL 허용 (비어 있을 수 있음)
# 타입 힌트가 곧 nullable 여부라서, 편집기 자동완성·타입 검사도 이 정보를 그대로 쓴다.


class BidAnnouncement(Base):
    """
    입찰공고 테이블 ─ "이런 공사가 나왔습니다." 게시글 한 장
    (02_erd.md 4.1절 기준)
    """
    __tablename__ = "bid_announcements"

    # id: 방마다 붙는 고유 호실 번호. API 원본 fields를 PK로 사용하지 않는 이유:
    # ERD에 작성된 대로 ─ 추후 식별 규칙이 바뀌어도 이 번호는 바뀌지 않는다.
    id: Mapped[int] = mapped_column(primary_key=True)

    # 공고번호 + 공고차수 = 실제 신분증. 정정·재공고되면 번호는 그대로이고 차수만 오른다 (DEVLOG 2026-09-13 실측)
    bid_ntce_no: Mapped[str] = mapped_column(String(40))
    bid_ntce_ord: Mapped[str] = mapped_column(String(3), default="000")

    bid_ntce_nm: Mapped[str] = mapped_column(String(1000))  # 공고명 ─ 공종을 찾지 못하면 여기서 키워드를 추출한다. (M2)
    ntce_instt_nm: Mapped[str | None] = mapped_column(String(400))  # 공고기관명
    dminstt_nm: Mapped[str | None] = mapped_column(String(400))     # 수요기관명

    # 지역 분석의 기준 필드. dminstt_nm(수요기관 소재지)이 아니라
    # 이 필드를 사용하는 이유는 "실제로 공사가 이뤄지는 곳"이 맞기 때문 (02_erd.md 5.2절)
    cnstrtsite_rgn_nm: Mapped[str | None] = mapped_column(String(200))

    # 수의계약 건에서는 비어있음 (02_erd.md 5.2절 실측 확인)
    main_cnstty_nm: Mapped[str | None] = mapped_column(String(300))

    cntrct_ccncls_mthd_nm: Mapped[str | None] = mapped_column(String(500))  # 계약체결방법 ─ main_cnstty_nm이 비어있는 이유를 설명해줌

    # 면허제한정보의 첫 번째 면허 이름 (2026-10-26 추가, 마이그레이션 0003). 공종 분류의 2차 출처.
    # 수의계약처럼 main_cnstty_nm이 빈 공고도 87%는 여기에 업종이 있다 (DEVLOG 2026-10-26 사전 검증).
    # 원본으로 저장해 두어야 분류 규칙을 고쳤을 때 API를 다시 부르지 않고 재분류할 수 있다.
    lcns_lmt_nm: Mapped[str | None] = mapped_column(String(200))

    # 금액은 BIGINT. 수백억짜리 공사가 있어서 INTEGER 범위(약 21억)를 넘을 수 있음
    bdgt_amt: Mapped[int | None] = mapped_column(BigInteger)
    presmpt_prce: Mapped[int | None] = mapped_column(BigInteger)

    # API가 주는 일시는 한국 시간(KST) 그대로 저장한다.
    bid_ntce_dt: Mapped[datetime | None]  # 공고일시 ─ 기간 필터 기준
    openg_dt: Mapped[datetime | None]     # 개찰일시 ─ 개찰일시가 지나야 낙찰결과가 생김

    # 수집 meta data. "내가 언제 이 데이터를 가져왔는지" ─ API가 준 값이 아니고 직접 기록한다. (UTC)
    fetched_at: Mapped[datetime] = mapped_column(default=utcnow)

    # ── M2 정제 결과 (2026-10-26 추가, 마이그레이션 0002) ──
    # 원본은 그대로 두고 손질한 값을 옆 칸에 따로 적는다. 규칙을 고치면 원본에서 다시 계산할 수 있게.
    # 시/도 짧은 이름 ("서울", "전남광주" …). 지역별 GROUP BY·필터 기준이라 인덱스 (04_api_spec.md 3.2절)
    region_normalized: Mapped[str | None] = mapped_column(String(20))
    # 공종 대분류 ("건축", "토목" … "기타"). 분류 못하면 NULL
    category: Mapped[str | None] = mapped_column(String(20))
    # 분류 출처 ─ main_cnstty(업종) / license(면허제한) / keyword(공고명으로 추정) / none(분류 못함). 화면의 "추정" 배지 근거
    category_source: Mapped[str | None] = mapped_column(String(20))

    # 1:0..1 관계의 "1"쪽. 낙찰결과 하나(또는 0개)를 들여다볼 수 있는 창문
    # 타입이 "BidResult | None"이라 SQLAlchemy가 "list가 아니라 하나 or 없음"으로 다룬다. (예전의 uselist=False)
    result: Mapped["BidResult | None"] = relationship(back_populates="announcement")

    __table_args__ = (
        # 같은 공고가 중복 수집 되어도 Row가 늘어나지 않도록 막는 핵심 제약
        UniqueConstraint("bid_ntce_no", "bid_ntce_ord", name="uq_bid_announcement"),
        # 지역별 GROUP BY가 잦으니 INDEX. (전화번호부에 색인을 붙이는 것과 같은 원리)
        Index("ix_cnstrtsite_rgn_nm", "cnstrtsite_rgn_nm"),
        Index("ix_bid_ntce_dt", "bid_ntce_dt"),
        Index("ix_region_normalized", "region_normalized"),
    )


class BidResult(Base):
    """
    낙찰결과 테이블 ─ "해당 공사를 누가 얼마에 낙찰해 갔는지"의 발표문
    개찰 전이거나 유찰된 공고는 이 Table에 Row가 아예 없음 (fields가 null이 아니고 Row 값 자체가 없음)
    """
    __tablename__ = "bid_results"

    id: Mapped[int] = mapped_column(primary_key=True)

    # 어떤 공고의 결과인지 ─ unique=True 가 핵심.
    # 이 fields가 있어야 "1:0..1"이 DB 레벨에서 강제됨 (한 공고에 결과값이 두 번 붙는 걸 원천 차단한다.)
    announcement_id: Mapped[int] = mapped_column(ForeignKey("bid_announcements.id"), unique=True)

    # 조회 편의용 중복 저장 ─ JOIN 없이 공고번호로 바로 찾고 싶을 때
    bid_ntce_no: Mapped[str] = mapped_column(String(40))
    bid_ntce_ord: Mapped[str] = mapped_column(String(3))

    bidwinnr_nm: Mapped[str | None] = mapped_column(String(200))  # 최종낙찰업체명
    sucsfbid_amt: Mapped[int | None] = mapped_column(BigInteger)  # 최종낙찰금액

    # NUMERIC(6,3) ─ FLOAT 대신 NUMERIC을 사용하는 이유: 낙찰률은 평균·집계의 핵심 지표다.
    # 즉, 부동소수점 오차가 누적되면 안됨. 999.999까지 정확하게 표현 가능
    sucsfbid_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))

    prtcpt_cnum: Mapped[int | None]       # 참가업체수
    rl_openg_dt: Mapped[datetime | None]  # 실개찰일시
    fnl_sucsf_date: Mapped[date | None]   # 최종낙찰일자

    fetched_at: Mapped[datetime] = mapped_column(default=utcnow)

    # "1"쪽에서 나를 가리키는 창문(result)과 짝을 맞추는 반대편 창문
    announcement: Mapped["BidAnnouncement"] = relationship(back_populates="result")
