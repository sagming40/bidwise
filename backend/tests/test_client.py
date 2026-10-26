# 나라장터 클라이언트 테스트. 실제 API는 부르지 않는다 (하루 1,000건 한도).
# requests.get 자리에 "가짜 응답을 돌려주는 함수"를 끼워 넣어서, 우리 코드의 판단만 검사한다.

import pytest

from app.collector import client


class FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise client.requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def make_page(items, total_count, page_no=1) -> dict:
    return {
        "response": {
            "header": {"resultCode": "00", "resultMsg": "정상"},
            "body": {"items": items, "numOfRows": len(items), "pageNo": page_no, "totalCount": total_count},
        }
    }


def test_인증키는_params로_넘긴다(monkeypatch, announcements_page):
    # 인증키를 URL 문자열에 직접 붙이지 않고 params로 넘겨야 requests가 한 번만 인코딩한다.
    calls = []

    def fake_get(url, params, timeout):
        calls.append(params)
        return FakeResponse(announcements_page)

    monkeypatch.setattr(client.requests, "get", fake_get)

    client.fetch_announcements_page("202609010000", "202609052359")

    assert calls[0]["serviceKey"] == "test-key"
    assert calls[0]["inqryBgnDt"] == "202609010000"


def test_낙찰정보는_공고일시_기준으로_조회한다(monkeypatch, real_results_page):
    # 낙찰정보의 inqryDiv=1은 "결과 등록일"이라 같은 기간의 공고와 안 맞는다. 2(공고일시)여야 한다.
    calls = []

    def fake_get(url, params, timeout):
        calls.append((url, params))
        return FakeResponse(real_results_page)

    monkeypatch.setattr(client.requests, "get", fake_get)

    items = client.fetch_all_results("202610200000", "202610202359")

    url, params = calls[0]
    assert "/as/ScsbidInfoService/getScsbidListSttusCnstwk" in url
    assert params["inqryDiv"] == "2"
    assert len(items) == 3


def test_resultCode가_00이_아니면_예외(monkeypatch):
    error_payload = {"response": {"header": {"resultCode": "03", "resultMsg": "NODATA_ERROR"}}}
    monkeypatch.setattr(client.requests, "get", lambda url, params, timeout: FakeResponse(error_payload))

    with pytest.raises(client.NaraJangteoAPIError, match=r"\[03\] NODATA_ERROR"):
        client.fetch_announcements_page("202609010000", "202609052359")


def test_시간_초과면_쉬었다가_다시_부른다(monkeypatch, announcements_page):
    attempts = []
    waits = []

    def flaky_get(url, params, timeout):
        attempts.append(timeout)
        if len(attempts) < 3:
            raise client.requests.ReadTimeout("느림")
        return FakeResponse(announcements_page)

    monkeypatch.setattr(client.requests, "get", flaky_get)
    monkeypatch.setattr(client.time, "sleep", waits.append)  # 테스트에서 진짜로 기다리지 않는다

    body = client.fetch_announcements_page("202609010000", "202609052359")

    assert len(attempts) == 3
    assert waits == [2, 4]
    assert body["totalCount"] == 2


def test_계속_시간_초과면_결국_예외(monkeypatch):
    def always_timeout(url, params, timeout):
        raise client.requests.ConnectTimeout("안 붙음")

    monkeypatch.setattr(client.requests, "get", always_timeout)
    monkeypatch.setattr(client.time, "sleep", lambda s: None)

    with pytest.raises(client.requests.ConnectTimeout):
        client.fetch_announcements_page("202609010000", "202609052359")


def test_HTTP_에러는_재시도하지_않는다(monkeypatch):
    # 인증 실패 같은 4xx는 다시 불러도 같다. 호출 한도만 버리지 않게 한 번에 끝낸다.
    attempts = []

    def fake_get(url, params, timeout):
        attempts.append(1)
        return FakeResponse({}, status_code=401)

    monkeypatch.setattr(client.requests, "get", fake_get)

    with pytest.raises(client.requests.HTTPError):
        client.fetch_announcements_page("202609010000", "202609052359")
    assert len(attempts) == 1


def test_HTTP_에러는_그대로_올린다(monkeypatch):
    monkeypatch.setattr(client.requests, "get", lambda url, params, timeout: FakeResponse({}, status_code=500))

    with pytest.raises(client.requests.HTTPError):
        client.fetch_announcements_page("202609010000", "202609052359")


def test_전체_개수만큼_페이지를_넘기며_모은다(monkeypatch):
    # 총 5건, 페이지당 2건 → 3페이지(2+2+1)를 받고 멈춰야 한다.
    pages = {
        1: make_page([{"bidNtceNo": "A"}, {"bidNtceNo": "B"}], 5, 1),
        2: make_page([{"bidNtceNo": "C"}, {"bidNtceNo": "D"}], 5, 2),
        3: make_page([{"bidNtceNo": "E"}], 5, 3),
    }
    requested_pages = []

    def fake_get(url, params, timeout):
        page_no = int(params["pageNo"])
        requested_pages.append(page_no)
        return FakeResponse(pages[page_no])

    monkeypatch.setattr(client.requests, "get", fake_get)

    items = client.fetch_all_announcements("202609010000", "202609052359", num_of_rows=2)

    assert [item["bidNtceNo"] for item in items] == ["A", "B", "C", "D", "E"]
    assert requested_pages == [1, 2, 3]


def test_결과가_0건이면_items가_빈_문자열이어도_빈_리스트(monkeypatch):
    # 나라장터는 0건일 때 items를 [] 가 아니라 "" 로 준다.
    monkeypatch.setattr(client.requests, "get", lambda url, params, timeout: FakeResponse(make_page("", 0)))

    assert client.fetch_all_announcements("202609010000", "202609052359") == []


def test_정정공고는_같은_번호에_차수만_다르다(monkeypatch, announcements_page):
    # UPSERT 기준이 (bidNtceNo, bidNtceOrd)여야 하는 이유를 데이터로 고정해 둔다.
    monkeypatch.setattr(client.requests, "get", lambda url, params, timeout: FakeResponse(announcements_page))

    items = client.fetch_all_announcements("202609010000", "202609052359")
    keys = [(item["bidNtceNo"], item["bidNtceOrd"]) for item in items]

    assert len({no for no, _ in keys}) == 1
    assert len(set(keys)) == 2
