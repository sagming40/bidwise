# 이 파일의 역할 ─ 지역명 정규화
# "경상북도 안동시" → "경북". 지도·지역별 집계는 시/도 단위라서 짧은 이름 하나로 묶는다.

import logging

logger = logging.getLogger(__name__)

# 공사현장지역명의 첫 단어(시/도) → 짧은 이름.
# 2026-10-26 실측(공고 10,285건): 첫 단어가 항상 아래 16개 중 하나였다. NULL·여러 지역이 섞인 값 없음.
REGION_NAMES = {
    "서울특별시": "서울",
    "부산광역시": "부산",
    "대구광역시": "대구",
    "인천광역시": "인천",
    "대전광역시": "대전",
    "울산광역시": "울산",
    "세종특별자치시": "세종",
    "경기도": "경기",
    "강원특별자치도": "강원",
    "충청북도": "충북",
    "충청남도": "충남",
    "전북특별자치도": "전북",
    "경상북도": "경북",
    "경상남도": "경남",
    "제주특별자치도": "제주",
    # 광주와 전남은 하나로 통합되어 API도 이 이름 하나로 준다. 시/도만 적힌 공고(104건)는
    # 광주인지 전남인지 알 수 없어서, 나누지 않고 통합 지역 하나로 본다 (DEVLOG 2026-10-26 M2 사전 검증)
    "전남광주통합특별시": "전남광주",
    # 예전 이름. 지금 데이터엔 없지만 과거 공고를 수집하면 나올 수 있어 지금 이름으로 모은다.
    "강원도": "강원",
    "전라북도": "전북",
    "광주광역시": "전남광주",
    "전라남도": "전남광주",
}


def normalize_region(cnstrtsite_rgn_nm: str | None) -> str | None:
    """
    공사현장지역명 → 시/도 짧은 이름. 모르는 시/도면 None을 주고 경고를 남긴다.
    (모르는 값에서 예외를 내면 그 하루치 수집이 통째로 멈추므로, 비워 두고 로그로 알린다.
     NULL인 행은 SELECT ... WHERE region_normalized IS NULL로 바로 찾을 수 있다)
    """
    if not cnstrtsite_rgn_nm:
        return None
    first_word = cnstrtsite_rgn_nm.split()[0]
    region = REGION_NAMES.get(first_word)
    if region is None:
        logger.warning("모르는 시/도: %r", cnstrtsite_rgn_nm)
    return region
