# 이 파일의 역할 ─ "시장에 다녀오는 직원"
# 하는 일: API 호출, 페이징, 원본 JSON을 그대로 return
# 하지 않는 일: 데이터 해석, 지역명 정리, 공사분류 정리, DB 저장(→ repository)

import logging

import requests

from app.config import get_settings

# print 대신 logger를 쓰는 이유: 나중에 스케줄러가 사람 없이 돌릴 때도 기록이 남아야 하고,
# 어느 파일에서 나온 메시지인지(__name__)와 시각이 함께 찍힌다.
logger = logging.getLogger(__name__)

BID_ANNOUNCEMENT_URL = (
    "https://apis.data.go.kr/1230000/ad/BidPublicInfoService/"
    "getBidPblancListInfoCnstwk"
)


class NaraJangteoAPIError(Exception):
    """
    통신을 성공했지만 내용상 Error인 경우 나라장터 API에서 발생시키는 예외.
    비유: 택배는 정상적으로 도착했는데(HTTP 200), 상자 안이 텅 비어 있는 상태.
    배송 실패(HTTP 에러)가 아니라 상자 내용물을 확인해야 알 수 있는 에러라서 따로 구분한다.
    """
    pass


def _call_api(url: str, params: dict) -> dict:
    """
    두 API(입찰/낙찰정보)가 똑같은 요청·응답 뼈대를 사용하기 때문에,
    실제 HTTP 통신은 이 함수 한 곳에서만 한다.
    추후 낙찰정보 클라이언트를 만들 때에도 이 함수를 그대로 재사용한다.
    """
    # 인증키는 여기서 한 번만 붙인다. params로 넘기면 requests가 URL 인코딩을 해주므로
    # .env에는 % 없는 원본 키를 넣어야 한다 (인코딩된 키는 이중 인코딩되어 인증 실패).
    params = {"serviceKey": get_settings().data_go_kr_service_key, **params}
    response = requests.get(url, params=params, timeout=10)

    # HTTP 레벨 에러(404, 500 등)는 이 곳에서 바로 예외로 터뜨린다.
    # 이 함수가 없으면 "response.json()이 이상하다"는 엉뚱한 error로 이어질 수 있다.
    response.raise_for_status()

    data = response.json()

    # HTTP는 200을 받았으나, API 자체 로직에서는 실패인 경우가 있다.
    # 예: 인증키는 맞는데 날짜 형식이 틀렸다 → 통신은 됐지만 내용이 error
    result_code = data["response"]["header"]["resultCode"]
    if result_code != "00":
        result_msg = data["response"]["header"]["resultMsg"]
        raise NaraJangteoAPIError(f"[{result_code}] {result_msg}")

    return data["response"]["body"]


def fetch_announcements_page(begin_dt: str, end_dt: str, page_no: int = 1, num_of_rows: int = 100) -> dict:
    """
    입찰공고 목록에서 딱 1페이지만 가져온다.
    begin_dt, end_dt 형식: "YYYYMMDDHHMM" (12자리, 예: "202609010000")
    """
    params = {
        "type": "json",
        "inqryDiv": "1",  # 1 = 공고게시일시 기준 조회
        "inqryBgnDt": begin_dt,
        "inqryEndDt": end_dt,
        "pageNo": str(page_no),
        "numOfRows": str(num_of_rows),
    }
    return _call_api(BID_ANNOUNCEMENT_URL, params)


def fetch_all_announcements(begin_dt: str, end_dt: str, num_of_rows: int = 100) -> list[dict]:
    """
    기간 안의 공고를 페이지 끝까지 전부 모아서 반환한다.
    비유: 도서관에서 1상자에 100권 씩 지원받기로 했다.
    맨 처음 상자에 도서관에서 총 몇 권을 보내줄지 적혀있다.
    즉, 첫 상자를 받아보고 받을 책이 총 몇 권인지 확인한 후 나머지 상자를 계속 요청하는 식이다.

    ⚠️ 페이지 1장 = API 호출 1번. 하루 한도(1,000건)가 빠듯하니 num_of_rows는 크게 잡는다.
    (2026-09-13 실측: 같은 기간이 10건씩이면 394번, 200건씩이면 20번)
    """
    all_items: list[dict] = []
    page_no = 1

    while True:
        body = fetch_announcements_page(begin_dt, end_dt, page_no, num_of_rows)
        total_count = body["totalCount"]

        # ⚠️ 나라장터 응답의 함정: 결과가 0건이면 "items"가 list가 아니라
        # 빈 문자열로 온다. list로 올 걸 가정하고 바로 순회하면 TypeError가 난다.
        # ─ 빈 데이터를 방어적으로 다뤄야 하는 전형적인 공공 API 패턴
        items = body.get("items", [])
        if isinstance(items, str):
            items = []

        all_items.extend(items)

        logger.info("페이지 %d: %d건 (누적 %d/%d)", page_no, len(items), len(all_items), total_count)

        # 지금까지 모은 개수가 전체 개수 이상이면 수집(반복) 종료
        if len(all_items) >= total_count or len(items) == 0:
            break

        page_no += 1

    return all_items
