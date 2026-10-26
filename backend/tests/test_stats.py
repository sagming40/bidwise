# 집계 쿼리 테스트. LEFT JOIN이라 결과 없는 공고도 세는지, 기간 끝날이 포함되는지.

from datetime import date, datetime
from decimal import Decimal

import pytest

from app.repository import bid_repo


def ann(no, day, region, category=None, source="none", budget=100):
    return {"bid_ntce_no": no, "bid_ntce_ord": "000", "bid_ntce_nm": "공사", "bdgt_amt": budget,
            "bid_ntce_dt": datetime(2026, 10, day, 15, 0), "region_normalized": region,
            "category": category, "category_source": source}


def res(no, rate):
    return {"bid_ntce_no": no, "bid_ntce_ord": "000", "bidwinnr_nm": "OO", "sucsfbid_amt": 1,
            "sucsfbid_rate": None if rate is None else Decimal(rate), "prtcpt_cnum": 1,
            "rl_openg_dt": None, "fnl_sucsf_date": None}


@pytest.fixture
def filled(session):
    """
    10-01 ~ 10-03 공고 5건. 결과는 3건 (그중 1건은 낙찰률 없음). 10-04 공고 1건은 기간 밖.
    """
    bid_repo.upsert_announcements(session, [
        ann("A1", 1, "서울", "건축", "main_cnstty"),
        ann("A2", 2, "서울", "토목", "keyword"),
        ann("A3", 3, "경기", "건축", "keyword"),
        ann("A4", 3, "경기"),                      # 미분류
        ann("A5", 3, "제주", "토목", "main_cnstty"),  # 결과 없음 → 제주 평균은 None
        ann("A6", 4, "서울", "건축", "main_cnstty"),  # 기간 밖
    ])
    bid_repo.upsert_results(session, [res("A1", "90.000"), res("A2", "86.000"), res("A3", None), res("A6", "50.000")])
    session.commit()
    return session


PERIOD = (date(2026, 10, 1), date(2026, 10, 3))


def test_요약은_결과_없는_공고도_센다(filled):
    s = bid_repo.get_summary(filled, *PERIOD)

    assert s["total_announcements"] == 5   # 10-04는 빠지고, 10-03 오후 공고는 들어간다 (끝날 포함)
    assert s["completed_count"] == 3
    assert s["pending_count"] == 2
    assert s["avg_sucsfbid_rate"] == pytest.approx(88.0)  # 낙찰률 없는 A3는 평균에서 빠진다
    assert s["total_budget_amt"] == 500


def test_요약_지역_필터(filled):
    assert bid_repo.get_summary(filled, *PERIOD, region="경기")["total_announcements"] == 2


def test_지역별은_결과가_없는_지역도_포함(filled):
    by_region = {r["region"]: r for r in bid_repo.get_region_stats(filled, *PERIOD)}

    assert set(by_region) == {"서울", "경기", "제주"}
    assert by_region["서울"]["total_count"] == 2
    assert by_region["서울"]["completed_count"] == 2
    assert by_region["제주"]["completed_count"] == 0
    assert by_region["제주"]["avg_sucsfbid_rate"] is None  # 지도에서 "데이터 없음" 색


def test_공종별은_미분류와_추정_건수를_준다(filled):
    by_cat = {r["category"]: r for r in bid_repo.get_category_stats(filled, *PERIOD)}

    assert by_cat["건축"]["total_count"] == 2
    assert by_cat["건축"]["keyword_count"] == 1
    assert by_cat["토목"]["keyword_count"] == 1
    assert by_cat["미분류"]["total_count"] == 1


def test_공종별_지역_필터와_개수_제한(filled):
    rows = bid_repo.get_category_stats(filled, *PERIOD, region="서울", limit=1)

    assert len(rows) == 1
    assert rows[0]["total_count"] == 1
