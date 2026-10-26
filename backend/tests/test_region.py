# 지역명 정규화 테스트

import pytest

from app.transformer.region import normalize_region


@pytest.mark.parametrize("raw, expected", [
    ("서울특별시", "서울"),
    ("경상북도 안동시", "경북"),
    ("강원특별자치도 춘천시", "강원"),
    ("세종특별자치시", "세종"),
    ("부산광역시 부산진구", "부산"),  # 실제 응답 fixture 값
])
def test_첫_단어로_시도를_정한다(raw, expected):
    assert normalize_region(raw) == expected


@pytest.mark.parametrize("raw", ["전남광주통합특별시", "전남광주통합특별시 광산구", "전남광주통합특별시 여수시"])
def test_광주와_전남은_통합_지역_하나(raw):
    # 시/도만 적힌 공고는 광주인지 전남인지 알 수 없어서 나누지 않는다 (DEVLOG 2026-10-26)
    assert normalize_region(raw) == "전남광주"


@pytest.mark.parametrize("raw, expected", [("광주광역시 북구", "전남광주"), ("전라남도 목포시", "전남광주"),
                                           ("전라북도 전주시", "전북"), ("강원도 원주시", "강원")])
def test_예전_이름도_지금_이름으로(raw, expected):
    assert normalize_region(raw) == expected


def test_모르는_시도나_빈_값은_None(caplog):
    assert normalize_region(None) is None
    assert normalize_region("") is None
    assert normalize_region("화성특별시 어딘가") is None
    assert "모르는 시/도" in caplog.text
