# 이 파일의 역할 ─ "재료 손질하는 주방 보조" (입찰공고 담당)
# 하는 일: API 원본 dict(전부 문자열) → DB 컬럼 이름·타입에 맞춘 dict
# 하지 않는 일: API 호출(→ collector), DB 저장(→ repository)
# 지역 정규화·공종 분류도 Transformer 일이지만 M2 작업이라 아직 없다.

from app.transformer.convert import to_datetime, to_int, to_str


def to_announcement_row(item: dict) -> dict:
    """
    입찰공고 API 항목 하나 → bid_announcements 행 하나.
    API 응답에는 필드가 143개 있지만, ERD(02_erd.md 4.1절)에서 고른 12개만 옮겨 담는다.
    id·fetched_at은 DB와 repository가 채운다.
    """
    return {
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
    }
