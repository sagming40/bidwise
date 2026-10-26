# 입찰공고 변환 테스트. API 원본(전부 문자열) → DB 행(int·datetime·None)으로 바뀌는지 본다.

from datetime import datetime

import pytest

from app.transformer.announcement import to_announcement_row


def test_실제_응답을_DB_행으로_바꾼다(real_announcements_page):
    item = real_announcements_page["response"]["body"]["items"][0]

    row = to_announcement_row(item)

    assert row["bid_ntce_no"] == "R26BK01779808"
    assert row["bid_ntce_ord"] == "000"
    assert row["cnstrtsite_rgn_nm"] == "부산광역시 부산진구"
    assert row["cntrct_ccncls_mthd_nm"] == "수의계약"
    assert row["bdgt_amt"] == 84610000
    assert row["presmpt_prce"] == 76918182
    assert row["bid_ntce_dt"] == datetime(2026, 10, 20, 1, 19, 37)
    assert row["openg_dt"] == datetime(2026, 10, 26, 13, 0, 0)


def test_실제_응답의_빈_문자열은_None(real_announcements_page):
    # 수의계약 건은 mainCnsttyNm이 ""로 온다 (02_erd.md 5.2절). ""가 아니라 NULL로 저장해야 한다.
    for item in real_announcements_page["response"]["body"]["items"]:
        assert to_announcement_row(item)["main_cnstty_nm"] is None


def test_DB_컬럼에_맞는_키만_남긴다(real_announcements_page):
    # 143개 필드 중 ERD에서 고른 것 + M2 정제 결과. id·fetched_at은 DB·repository가 채운다.
    row = to_announcement_row(real_announcements_page["response"]["body"]["items"][0])

    assert set(row) == {
        "bid_ntce_no", "bid_ntce_ord", "bid_ntce_nm", "ntce_instt_nm", "dminstt_nm",
        "cnstrtsite_rgn_nm", "main_cnstty_nm", "cntrct_ccncls_mthd_nm",
        "bdgt_amt", "presmpt_prce", "bid_ntce_dt", "openg_dt",
        "lcns_lmt_nm", "region_normalized", "category", "category_source",
    }


def test_수집할_때_지역과_공종도_정한다(real_announcements_page):
    items = real_announcements_page["response"]["body"]["items"]
    rows = [to_announcement_row(item) for item in items]

    assert [r["region_normalized"] for r in rows] == ["부산", "경북", "경기"]
    # 3건 모두 업종이 비어 있는 수의계약이라 1차 분류는 안 된다 → keyword 또는 none
    assert all(r["category_source"] in {"keyword", "none"} for r in rows)


def test_빠진_필드와_빈_값은_None_차수는_000():
    row = to_announcement_row({"bidNtceNo": "X1", "bidNtceNm": "테스트 공사", "bidNtceOrd": "", "bdgtAmt": " "})

    assert row["bid_ntce_ord"] == "000"
    assert row["bdgt_amt"] is None
    assert row["openg_dt"] is None
    assert row["dminstt_nm"] is None


def test_소수점_붙은_금액도_정수로():
    row = to_announcement_row({"bidNtceNo": "X1", "bidNtceNm": "테스트 공사", "presmptPrce": "12345000000.0"})

    assert row["presmpt_prce"] == 12345000000


def test_모르는_날짜_형식은_조용히_넘기지_않는다():
    with pytest.raises(ValueError):
        to_announcement_row({"bidNtceNo": "X1", "bidNtceNm": "테스트 공사", "bidNtceDt": "20261020"})


def test_면허를_넘겨주면_면허로_분류한다(real_announcements_page, real_license_page):
    from app.transformer.license import first_license_by_announcement

    licenses = first_license_by_announcement(real_license_page["response"]["body"]["items"])
    item = real_announcements_page["response"]["body"]["items"][0]  # R26BK01779808, 업종 없는 수의계약

    row = to_announcement_row(item, licenses.get((item["bidNtceNo"], item["bidNtceOrd"])))

    assert row["lcns_lmt_nm"] == "기계설비ㆍ가스공사업"
    assert (row["category"], row["category_source"]) == ("기계설비", "license")
