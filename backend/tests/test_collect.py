# 수집 기간 나누기 테스트. 긴 기간을 하루씩 잘라야 실패해도 그날만 다시 돌리면 된다.

from app import collect


def test_하루_안이면_그대로():
    assert collect.split_by_day("202610200000", "202610202359") == [("202610200000", "202610202359")]


def test_여러_날이면_하루씩_자른다():
    assert collect.split_by_day("202609300900", "202610021200") == [
        ("202609300900", "202609302359"),  # 첫날은 시작 시각부터
        ("202610010000", "202610012359"),  # 월이 바뀌어도
        ("202610020000", "202610021200"),  # 마지막 날은 끝 시각까지
    ]


def test_한_달이면_30구간():
    windows = collect.split_by_day("202609260000", "202610252359")

    assert len(windows) == 30
    assert windows[0] == ("202609260000", "202609262359")
    assert windows[-1] == ("202610250000", "202610252359")


def test_하루씩_collect를_부르고_합계를_낸다(monkeypatch):
    called = []

    def fake_collect(begin_dt, end_dt):
        called.append(begin_dt[:8])
        return {"announcements": 10, "results": 2, "results_skipped": 1}

    monkeypatch.setattr(collect, "collect", fake_collect)

    totals = collect.collect_by_day("202610010000", "202610032359")

    assert called == ["20261001", "20261002", "20261003"]
    assert totals == {"announcements": 30, "results": 6, "results_skipped": 3}
