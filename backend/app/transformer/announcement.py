# 이 파일의 역할 ─ "재료 손질하는 주방 보조"
# 하는 일: API 원본 dict(전부 문자열) → DB 컬럼 이름·타입에 맞춘 dict
# 하지 않는 일: API 호출(→ collector), DB 저장(→ repository)
# 지역 정규화·공종 분류도 Transformer 일이지만 M2 작업이라 아직 없다.

from datetime import datetime
from decimal import Decimal

# 나라장터 일시 형식. 2026-10-20 실측: bidNtceDt·opengDt 모두 "2026-10-20 01:19:37"
API_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _to_str(value: str | None) -> str | None:
    """
    나라장터는 값이 없을 때 null이 아니라 빈 문자열("")을 준다 (예: 수의계약 건의 mainCnsttyNm).
    ""를 그대로 저장하면 "값이 없음"을 SQL에서 IS NULL로 못 찾으므로 None으로 바꾼다.
    """
    if value is None:
        return None
    value = value.strip()
    return value or None


def _to_int(value: str | None) -> int | None:
    """
    금액 문자열 → int. 실측은 "84610000"처럼 정수 문자열이지만,
    "84610000.0" 같은 값이 와도 깨지지 않게 Decimal을 거친다 (float를 거치면 큰 금액에서 오차가 날 수 있다).
    """
    value = _to_str(value)
    return None if value is None else int(Decimal(value))


def _to_datetime(value: str | None) -> datetime | None:
    """
    일시 문자열 → datetime. API가 주는 한국 시간(KST) 그대로, 시간대 없이 저장한다 (models.py 참고).
    형식이 다르면 None으로 덮지 않고 ValueError를 낸다 ─ 조용히 비워 두면 기간 필터에서 공고가 사라져도 모른다.
    """
    value = _to_str(value)
    return None if value is None else datetime.strptime(value, API_DATETIME_FORMAT)


def to_announcement_row(item: dict) -> dict:
    """
    입찰공고 API 항목 하나 → bid_announcements 행 하나.
    API 응답에는 필드가 143개 있지만, ERD(02_erd.md 4.1절)에서 고른 12개만 옮겨 담는다.
    id·fetched_at은 DB와 repository가 채운다.
    """
    return {
        "bid_ntce_no": item["bidNtceNo"],
        # 차수가 비어 오면 모델 기본값과 같은 "000"으로 본다. UPSERT 기준이라 NULL이면 안 된다.
        "bid_ntce_ord": _to_str(item.get("bidNtceOrd")) or "000",
        "bid_ntce_nm": item["bidNtceNm"],
        "ntce_instt_nm": _to_str(item.get("ntceInsttNm")),
        "dminstt_nm": _to_str(item.get("dminsttNm")),
        "cnstrtsite_rgn_nm": _to_str(item.get("cnstrtsiteRgnNm")),
        "main_cnstty_nm": _to_str(item.get("mainCnsttyNm")),
        # API 필드는 Cncls, 컬럼은 ccncls ─ M0 모델 이름을 그대로 따른다.
        "cntrct_ccncls_mthd_nm": _to_str(item.get("cntrctCnclsMthdNm")),
        "bdgt_amt": _to_int(item.get("bdgtAmt")),
        "presmpt_prce": _to_int(item.get("presmptPrce")),
        "bid_ntce_dt": _to_datetime(item.get("bidNtceDt")),
        "openg_dt": _to_datetime(item.get("opengDt")),
    }
