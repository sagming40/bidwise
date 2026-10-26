# 낙찰정보 변환 테스트. 낙찰률은 Decimal, 최종낙찰일자는 date, 빈 낙찰률은 None.

from datetime import date, datetime
from decimal import Decimal

from app.transformer.result import pick_final_results, to_result_row


def items_of(page: dict) -> list[dict]:
    return page["response"]["body"]["items"]


def test_실제_응답을_DB_행으로_바꾼다(real_results_page):
    row = to_result_row(items_of(real_results_page)[0])

    assert row == {
        "bid_ntce_no": "R26BK01780454",
        "bid_ntce_ord": "000",
        "bidwinnr_nm": "주식회사미성종합건설",
        "sucsfbid_amt": 49090000,
        "sucsfbid_rate": Decimal("89.99"),
        "prtcpt_cnum": 1,
        "rl_openg_dt": datetime(2026, 10, 20, 13, 13, 19),
        "fnl_sucsf_date": date(2026, 10, 20),
    }


def test_정수_낙찰률도_Decimal(real_results_page):
    # "90"처럼 소수점 없이 오는 값이 있다 (2026-10-26 실측)
    assert to_result_row(items_of(real_results_page)[1])["sucsfbid_rate"] == Decimal("90")


def test_빈_낙찰률은_None(real_results_page):
    # 낙찰금액은 있는데 낙찰률만 ""로 오는 결과가 있다. 평균에서 빠지도록 None.
    row = to_result_row(items_of(real_results_page)[2])

    assert row["sucsfbid_rate"] is None
    assert row["sucsfbid_amt"] == 20192000


def test_재입찰이_있으면_재입찰번호가_가장_큰_결과만_남긴다():
    items = [
        {"bidNtceNo": "A1", "bidNtceOrd": "000", "rbidNo": "001", "bidClsfcNo": "0", "bidwinnrNm": "재입찰 낙찰"},
        {"bidNtceNo": "A1", "bidNtceOrd": "000", "rbidNo": "000", "bidClsfcNo": "0", "bidwinnrNm": "처음 개찰"},
        {"bidNtceNo": "A1", "bidNtceOrd": "001", "rbidNo": "000", "bidClsfcNo": "0", "bidwinnrNm": "정정공고 쪽"},
    ]

    final = pick_final_results(items)

    assert sorted(i["bidwinnrNm"] for i in final) == ["재입찰 낙찰", "정정공고 쪽"]


def test_결과가_하나뿐이면_그대로(real_results_page):
    assert len(pick_final_results(items_of(real_results_page))) == 3
