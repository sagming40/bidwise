# 입찰공고 UPSERT 테스트. 임시 SQLite에 저장해 보고 행 수·값을 확인한다.
# (PostgreSQL 문법 쪽은 실제 DB에서 `python -m app.collect`를 두 번 돌려 확인한다)

from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select

from app.models import BidAnnouncement, BidResult
from app.repository import bid_repo
from app.transformer.announcement import to_announcement_row
from app.transformer.result import pick_final_results, to_result_row


def make_row(no: str, ord_: str = "000", name: str = "테스트 공사", **extra) -> dict:
    return {"bid_ntce_no": no, "bid_ntce_ord": ord_, "bid_ntce_nm": name, **extra}


def count(session) -> int:
    return session.scalar(select(func.count()).select_from(BidAnnouncement))


def test_같은_공고를_두_번_저장해도_행이_늘지_않는다(session, real_announcements_page):
    # M1 완료 기준 "두 번 연속 실행해도 행 수 불변"을 실제 응답 모양으로 확인
    rows = [to_announcement_row(item) for item in real_announcements_page["response"]["body"]["items"]]

    bid_repo.upsert_announcements(session, rows)
    session.commit()
    bid_repo.upsert_announcements(session, rows)
    session.commit()

    assert count(session) == 3


def test_이미_있는_공고는_새_값으로_고치고_id는_그대로(session):
    bid_repo.upsert_announcements(session, [make_row("A1", name="옛 이름", bdgt_amt=100)])
    session.commit()
    first = session.scalars(select(BidAnnouncement)).one()
    first_id, first_fetched_at = first.id, first.fetched_at

    bid_repo.upsert_announcements(session, [make_row("A1", name="새 이름", bdgt_amt=200)])
    session.commit()
    session.expire_all()  # 세션에 남은 옛 객체 말고 DB에서 다시 읽는다

    again = session.scalars(select(BidAnnouncement)).one()
    assert again.id == first_id  # id가 그대로여야 나중에 붙을 낙찰결과(announcement_id) 연결이 안 끊긴다
    assert again.bid_ntce_nm == "새 이름"
    assert again.bdgt_amt == 200
    assert again.fetched_at >= first_fetched_at


def test_정정공고는_차수가_다르면_별개의_행(session):
    bid_repo.upsert_announcements(session, [make_row("A1", "000"), make_row("A1", "001")])
    session.commit()

    assert count(session) == 2


def test_한_묶음_안의_중복은_나중_것만_남긴다(session):
    saved = bid_repo.upsert_announcements(session, [make_row("A1", name="먼저"), make_row("A1", name="나중")])
    session.commit()

    assert saved == 1
    assert session.scalars(select(BidAnnouncement.bid_ntce_nm)).one() == "나중"


def test_묶음_크기보다_많으면_나눠서_보낸다(session, monkeypatch):
    monkeypatch.setattr(bid_repo, "CHUNK_SIZE", 2)

    saved = bid_repo.upsert_announcements(session, [make_row(f"A{i}") for i in range(5)])
    session.commit()

    assert saved == 5
    assert count(session) == 5


def test_빈_목록이면_아무것도_안_한다(session):
    assert bid_repo.upsert_announcements(session, []) == 0
    assert count(session) == 0


def result_row(no: str, ord_: str = "000", rate: str | None = "90.123", winner: str = "OO건설") -> dict:
    return {
        "bid_ntce_no": no, "bid_ntce_ord": ord_, "bidwinnr_nm": winner,
        "sucsfbid_amt": 1000, "sucsfbid_rate": None if rate is None else Decimal(rate),
        "prtcpt_cnum": 3, "rl_openg_dt": None, "fnl_sucsf_date": None,
    }


def test_낙찰결과는_번호와_차수가_같은_공고에_붙는다(session):
    bid_repo.upsert_announcements(session, [make_row("A1", "000"), make_row("A1", "001")])
    session.flush()

    saved, skipped = bid_repo.upsert_results(session, [result_row("A1", "001")])
    session.commit()

    assert (saved, skipped) == (1, 0)
    corrected = session.scalars(select(BidAnnouncement).where(BidAnnouncement.bid_ntce_ord == "001")).one()
    original = session.scalars(select(BidAnnouncement).where(BidAnnouncement.bid_ntce_ord == "000")).one()
    assert corrected.result.sucsfbid_rate == Decimal("90.123")
    assert original.result is None  # 1:0..1 ─ 결과 없는 공고는 None


def test_낙찰결과를_두_번_저장해도_하나이고_새_값으로_고친다(session):
    bid_repo.upsert_announcements(session, [make_row("A1")])
    bid_repo.upsert_results(session, [result_row("A1", winner="처음")])
    session.commit()

    bid_repo.upsert_results(session, [result_row("A1", winner="나중")])
    session.commit()
    session.expire_all()

    assert session.scalar(select(func.count()).select_from(BidResult)) == 1
    assert session.scalars(select(BidResult.bidwinnr_nm)).one() == "나중"


def test_공고가_없는_낙찰결과는_건너뛴다(session):
    bid_repo.upsert_announcements(session, [make_row("A1")])

    saved, skipped = bid_repo.upsert_results(session, [result_row("A1"), result_row("ZZZ")])
    session.commit()

    assert (saved, skipped) == (1, 1)


def test_낙찰률이_없는_결과도_저장한다(session):
    bid_repo.upsert_announcements(session, [make_row("A1")])
    bid_repo.upsert_results(session, [result_row("A1", rate=None)])
    session.commit()

    assert session.scalars(select(BidResult.sucsfbid_rate)).one() is None


def test_실제_응답_낙찰결과를_공고에_연결(session, real_results_page):
    # 실제 응답의 공고번호로 공고를 먼저 만들고, 결과 3건이 전부 붙는지
    items = real_results_page["response"]["body"]["items"]
    bid_repo.upsert_announcements(session, [make_row(i["bidNtceNo"], i["bidNtceOrd"]) for i in items])

    saved, skipped = bid_repo.upsert_results(session, [to_result_row(i) for i in pick_final_results(items)])
    session.commit()

    assert (saved, skipped) == (3, 0)
    assert session.scalar(select(func.count()).select_from(BidResult)) == 3


def test_fetched_at은_저장할_때_채운다(session):
    # 행 dict에는 fetched_at이 없다. repository가 채워야 NOT NULL 컬럼에 들어간다.
    bid_repo.upsert_announcements(session, [make_row("A1")])
    session.commit()

    fetched_at = session.scalars(select(BidAnnouncement.fetched_at)).one()
    assert isinstance(fetched_at, datetime)
    assert fetched_at.tzinfo is None  # 시간대 없는 UTC (models.utcnow 참고)
