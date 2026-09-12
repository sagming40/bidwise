from sqlalchemy import (
    Column, Integer, String, BigInteger, Numeric,
    DateTime, Date, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

# Base = "이 아래에 있는 클래스들은 전부 진짜 테이블이다"라느 표지판
# SQLAlchemy가 이 표지판이 붙은 class들을 한데 모아 테이블을 생성해준다.
Base = declarative_base()


class BidAnnouncement(Base):
    """
    입찰공고 테이블 ─ "이런 공사가 나왔습니다." 게시글 한 장
    (02_erd.md 4.1절 기준)
    """
    __tablename__ = "bid_announcements"

    # id: 방마다 붙는 고유 호실 번호. API 원본 fields를 PK로 사용하지 않는 이유:
    # ERD에 작성된 대로 ─ 추후 식별 규칙이 바뀌어도 이 번호는 바뀌지 않는다.
    id = Column(Integer, primary_key=True)

    # 공고번호 + 공고차수 = 실제 신분증. 재공고되면 차수가 오름
    bid_ntce_no = Column(String(40), nullable=False)
    bid_ntce_ord = Column(String(3), nullable=False, default="000") 

    bid_ntce_nm = Column(String(1000), nullable=False)  # 공고명 ─ 공종을 찾지 못하면 여기서 키워드를 추축한다. (M2)
    ntce_instt_nm = Column(String(400))  # 공고기관명
    dminstt_nm = Column(String(400))     # 수요기관명

    # 지역 분석의 기준 필드. dminstt_nm(수요기관 소재지)이 아니라
    # 이 필드를 사용하는 이유는 "실제로 공사가 이뤄지는 곳"이 맞기 때문 (02_erd.md 5.2절)
    cnstrtsite_rgn_nm = Column(String(200))

    # 수의계약 건에서는 비어있음 (02_erd.md 5.2절 실측 확인)
    main_cnstty_nm = Column(String(300))

    cntrct_ccncls_mthd_nm = Column(String(500))  # 계약체결방법 ─ amin_cnstty_nm이 비어있는 이유를 설명해줌

    # 금액은 BIGINT. 수백억짜리 공사가 있어서 INTEGER 범위(약 21억)를 넘을 수 있음
    bdgt_amt = Column(BigInteger)
    presmpt_prce = Column(BigInteger)

    bid_ntce_dt = Column(DateTime)  # 공고일시 ─ 기간 필터 기준
    openg_dt = Column(DateTime)     # 개찰일지 ─ 개찰일시가 지나야 낙찰결과가 생김

    # 수집 meta data. "내가 언제 이 데이터를 가져왔는지" ─ API가 준 값이 아니고 직접 기록한다.
    fetched_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # 1:0..1 관계의 "1"쪽. 낙찰결과 하나(또는 0개)를 들여다볼 수 있는 창문
    # uselist=False = "list로 여러 개 X → 하나 or 0(None)"으로 다룬다.
    result = relationship("BidResult", back_populates="announcement", uselist=False)

    __table_args__ = (
        # 같은 공고가 중복 수집 되어도 Row가 늘어나지 않도록 막는 핵심 제약
        UniqueConstraint("bid_ntce_no", "bid_ntce_ord", name="uq_bid_announcement"),
        # 지역별 GROUP BY가 잦으니 INDEX. (전화번호부에 색인을 붙이는 것과 같은 원리)
        Index("ix_cnstrtsite_rgn_nm", "cnstrtsite_rgn_nm"),
        Index("ix_bid_ntce_dt", "bid_ntce_dt"),
    )


class BidResult(Base):
    """
    낙찰결과 테이블 ─ "해당 공사를 누가 얼마에 낙찰해 갔는지"의 발표문
    개찰 전이거나 유찰된 공고는 이 Table에 Row가 아예 없음 (fields가 null이 아니고 Row 값 자체가 없음)
    """
    __tablename__ = "bid_results"

    id = Column(Integer, primary_key=True)

    # 어떤 공고의 결과인지 ─ unique=True 가 핵심.
    # 이 fields가 있어야 "1:0..1"이 DB 레벨에서 강제됨 (한 공고에 결과값이 두 번 붙는 걸 원천 차단한다.)
    announcement_id = Column(
        Integer, ForeignKey("bid_announcements.id"), nullable=False, unique=True
    ) 

    # 조회 편의용 중복 저장 ─ JOIN 없이 공고번호로 바로 찾고 싶을 때
    bid_ntce_no = Column(String(40), nullable=False)
    bid_ntce_ord = Column(String(3), nullable=False)

    bidwinnr_nm = Column(String(200))       # 최종낙찰업체명
    sucsfbid_amt = Column(BigInteger)       # 최종낙찰금액

    # NUMERIC(6,3) ─ FLOAT 대신 NUMERIC을 사용하는 이유: 낙찰률은 평균·집계의 핵심 지표다.
    # 즉, 부동소수점 오차가 누적되면 안됨. 999.999까지 정확하게 표현 가능
    sucsfbid_rate = Column(Numeric(6, 3))

    prtcpt_cnum = Column(Integer)       # 참가업체수
    rl_openg_dt = Column(DateTime)      # 실개찰일시
    fnl_sucsf_date = Column(Date)       # 최종낙찰일자

    fetched_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # "1"쪽에서 나를 가리키는 창문(result)과 짝을 맞추는 반대편 창문
    announcement = relationship("BidAnnouncement", back_populates="result")
