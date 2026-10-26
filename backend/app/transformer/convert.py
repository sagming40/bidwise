# 이 파일의 역할 ─ "손질 도구 서랍"
# 나라장터는 숫자·날짜까지 전부 문자열로 준다. 문자열 하나를 DB 타입 하나로 바꾸는 작은 칼들을 모아 둔다.
# 입찰공고(announcement.py)와 낙찰정보(result.py)가 같이 쓴다.

from datetime import date, datetime
from decimal import Decimal

# 나라장터 일시·일자 형식. 2026-10-20·10-26 실측:
#   bidNtceDt·opengDt·rlOpengDt = "2026-10-20 01:19:37", fnlSucsfDate = "2026-10-20"
API_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
API_DATE_FORMAT = "%Y-%m-%d"


def to_str(value: str | None) -> str | None:
    """
    나라장터는 값이 없을 때 null이 아니라 빈 문자열("")을 준다 (예: 수의계약 건의 mainCnsttyNm).
    ""를 그대로 저장하면 "값이 없음"을 SQL에서 IS NULL로 못 찾으므로 None으로 바꾼다.
    """
    if value is None:
        return None
    value = value.strip()
    return value or None


def to_decimal(value: str | None) -> Decimal | None:
    """
    낙찰률 문자열 → Decimal. "90.205", "95", "87.91"처럼 소수 자릿수가 제각각이다 (2026-10-26 실측).
    float를 거치지 않는다 ─ NUMERIC(6,3)에 넣을 값이라 처음부터 십진수로 다룬다.
    """
    value = to_str(value)
    return None if value is None else Decimal(value)


def to_int(value: str | None) -> int | None:
    """
    금액·업체수 문자열 → int. 실측은 "84610000"처럼 정수 문자열이지만,
    "84610000.0" 같은 값이 와도 깨지지 않게 Decimal을 거친다 (float를 거치면 큰 금액에서 오차가 날 수 있다).
    """
    value = to_decimal(value)
    return None if value is None else int(value)


def to_datetime(value: str | None) -> datetime | None:
    """
    일시 문자열 → datetime. API가 주는 한국 시간(KST) 그대로, 시간대 없이 저장한다 (models.py 참고).
    형식이 다르면 None으로 덮지 않고 ValueError를 낸다 ─ 조용히 비워 두면 기간 필터에서 공고가 사라져도 모른다.
    """
    value = to_str(value)
    return None if value is None else datetime.strptime(value, API_DATETIME_FORMAT)


def to_date(value: str | None) -> date | None:
    """일자 문자열 → date. 형식이 다르면 to_datetime과 같은 이유로 ValueError."""
    value = to_str(value)
    return None if value is None else datetime.strptime(value, API_DATE_FORMAT).date()
