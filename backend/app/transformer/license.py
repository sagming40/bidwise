# 이 파일의 역할 ─ 면허제한정보 손질
# API 원본(공고 하나에 면허 행 여러 개, 물품·용역 섞임) → {(공고번호, 차수): 첫 번째 면허 이름}

from app.transformer.convert import to_str

# 면허제한정보에는 물품·용역 공고 것도 섞여 온다. 우리는 공사만 모은다.
CONSTRUCTION = "공사"


def _license_name(raw: str) -> str:
    """
    "기계설비ㆍ가스공사업/6202" → "기계설비ㆍ가스공사업". 뒤의 숫자는 업종 코드라 이름만 남긴다.
    (2026-10-20 실측 1,886행 전부 "이름/코드" 형식)
    """
    return raw.rsplit("/", 1)[0].strip()


def _order(item: dict) -> tuple[int, int]:
    """
    공고서에 적힌 면허 순서 = (제한그룹번호, 그룹 안 순번). 둘 다 숫자 문자열이라 int로 비교해야 한다.
    문자열로 비교하면 "10" < "2"가 되어 10번째 면허가 2번째보다 앞에 온다.
    """
    return int(item.get("lmtGrpNo") or 0), int(item.get("lmtSno") or 0)


def first_license_by_announcement(items: list[dict]) -> dict[tuple[str, str], str]:
    """
    공사 공고마다 첫 번째 면허 이름 하나.
    면허가 여러 개라 대분류가 갈리는 공고(하루 29건)에서 "첫 면허"와 "다수결"이 업종과 맞는 정도가
    27/29로 같아서, 설명하기 쉬운 "공고서에 처음 적힌 면허"를 쓴다 (DEVLOG 2026-10-26).
    """
    first: dict[tuple[str, str], dict] = {}
    for item in items:
        if item.get("bsnsDivNm") != CONSTRUCTION or not to_str(item.get("lcnsLmtNm")):
            continue
        key = (item["bidNtceNo"], to_str(item.get("bidNtceOrd")) or "000")
        if key not in first or _order(item) < _order(first[key]):
            first[key] = item
    return {key: _license_name(item["lcnsLmtNm"]) for key, item in first.items()}
