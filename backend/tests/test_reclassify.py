# 재분류 테스트. 정제 컬럼이 비어 있는 공고(마이그레이션 0002 직후 상태)를 채우고, 두 번 돌려도 같은지.

from sqlalchemy import select

from app.models import BidAnnouncement
from app.reclassify import reclassify
from app.repository import bid_repo


def make_row(no, rgn, industry, title):
    return {"bid_ntce_no": no, "bid_ntce_ord": "000", "bid_ntce_nm": title,
            "cnstrtsite_rgn_nm": rgn, "main_cnstty_nm": industry}


def test_빈_정제_컬럼을_채우고_두_번째는_바꿀_게_없다(session):
    bid_repo.upsert_announcements(session, [
        make_row("A1", "경상북도 안동시", "건축공사업", "OO 청사 신축"),
        make_row("A2", "전남광주통합특별시 광산구", None, "마을안 도로 포장공사"),
        make_row("A3", "서울특별시", None, "부안군 공고 제2026-1594호"),
    ])
    session.commit()

    first = reclassify()
    second = reclassify()

    assert first["changed"] == 3
    assert first["sources"] == {"main_cnstty": 1, "keyword": 1, "none": 1}
    assert second["changed"] == 0  # 바뀐 게 없으면 쓰지 않는다

    session.expire_all()
    got = {r.bid_ntce_no: (r.region_normalized, r.category, r.category_source)
           for r in session.scalars(select(BidAnnouncement))}
    assert got == {
        "A1": ("경북", "건축", "main_cnstty"),
        "A2": ("전남광주", "토목", "keyword"),
        "A3": ("서울", None, "none"),
    }


def test_규칙이_바뀌면_바뀐_행만_고친다(session, monkeypatch):
    bid_repo.upsert_announcements(session, [
        make_row("A1", "서울특별시", None, "마을안 도로 포장공사"),
        make_row("A2", "서울특별시", None, "OO 청사 신축"),
    ])
    session.commit()
    reclassify()

    # 규칙을 고쳤다고 치고: "도로"를 토목이 아니라 조경으로 (테스트용 가짜 규칙)
    from app.transformer import category
    rules = [("조경", ("도로",))] + category.KEYWORD_RULES
    monkeypatch.setattr(category, "KEYWORD_RULES", rules)

    assert reclassify()["changed"] == 1
