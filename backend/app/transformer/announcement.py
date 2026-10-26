# 이 파일의 역할 ─ "재료 손질하는 주방 보조" (입찰공고 담당)
# 하는 일: API 원본 dict(전부 문자열) → DB 컬럼 이름·타입에 맞춘 dict
# 하지 않는 일: API 호출(→ collector), DB 저장(→ repository)

from app.transformer.category import classify
from app.transformer.convert import to_datetime, to_int, to_str
from app.transformer.region import normalize_region


def classification_of(cnstrtsite_rgn_nm: str | None, main_cnstty_nm: str | None,
                      lcns_lmt_nm: str | None, bid_ntce_nm: str | None) -> dict:
    """
    원본 컬럼 4개 → M2 정제 컬럼 3개. 수집할 때도, 저장된 공고를 다시 분류할 때(reclassify.py)도 이 함수 하나를 쓴다.
    (두 곳에서 따로 계산하면 규칙을 고칠 때 한쪽만 바뀌는 사고가 난다)
    """
    category, source = classify(main_cnstty_nm, lcns_lmt_nm, bid_ntce_nm)
    return {
        "region_normalized": normalize_region(cnstrtsite_rgn_nm),
        "category": category,
        "category_source": source,
    }


def to_announcement_row(item: dict, lcns_lmt_nm: str | None = None) -> dict:
    """
    입찰공고 API 항목 하나 → bid_announcements 행 하나.
    API 응답에는 필드가 143개 있지만, ERD(02_erd.md 4.1절)에서 고른 12개만 옮겨 담고,
    면허제한정보의 첫 면허(별도 API라 따로 받아서 넘겨준다)와 M2 정제 결과(지역·공종) 3개를 덧붙인다.
    id·fetched_at은 DB와 repository가 채운다.
    """
    row = {
        "bid_ntce_no": item["bidNtceNo"],
        # 차수가 비어 오면 모델 기본값과 같은 "000"으로 본다. UPSERT 기준이라 NULL이면 안 된다.
        "bid_ntce_ord": to_str(item.get("bidNtceOrd")) or "000",
        "bid_ntce_nm": item["bidNtceNm"],
        "ntce_instt_nm": to_str(item.get("ntceInsttNm")),
        "dminstt_nm": to_str(item.get("dminsttNm")),
        "cnstrtsite_rgn_nm": to_str(item.get("cnstrtsiteRgnNm")),
        "main_cnstty_nm": to_str(item.get("mainCnsttyNm")),
        # API 필드는 Cncls, 컬럼은 ccncls ─ M0 모델 이름을 그대로 따른다.
        "cntrct_ccncls_mthd_nm": to_str(item.get("cntrctCnclsMthdNm")),
        "bdgt_amt": to_int(item.get("bdgtAmt")),
        "presmpt_prce": to_int(item.get("presmptPrce")),
        "bid_ntce_dt": to_datetime(item.get("bidNtceDt")),
        "openg_dt": to_datetime(item.get("opengDt")),
        "lcns_lmt_nm": lcns_lmt_nm,
    }
    row.update(classification_of(row["cnstrtsite_rgn_nm"], row["main_cnstty_nm"], lcns_lmt_nm, row["bid_ntce_nm"]))
    return row
