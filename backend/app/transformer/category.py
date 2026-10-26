# 이 파일의 역할 ─ 공종 분류 (3단계 폴백)
#   1차: 업종(main_cnstty_nm)이 있으면 업종 → 대분류               source = "main_cnstty"
#   2차: 없으면 면허제한정보의 첫 면허(lcns_lmt_nm) → 대분류         source = "license"
#   3차: 그것도 없으면 공고명(bid_ntce_nm) 키워드로 대분류를 추정     source = "keyword"
#   실패: 어느 쪽으로도 못 정하면 category = None                  source = "none"
#
# 2차(면허)는 2026-10-26 추가. 업종 없는 공고의 87%에 면허가 있고, 업종과 대분류가 96.4% 일치해서
# 키워드 추정(정확도 79%)보다 먼저 본다. 업종과 같은 이름 체계라 대분류 규칙(INDUSTRY_RULES)을 그대로 쓴다.
#
# main_cnstty_nm은 "공종"이 아니라 면허 업종 이름 47종이다 ("건축공사업", "산림사업법인(숲가꾸기 및 병해충방제)" …).
# 그대로 쓰면 차트 막대가 47개가 되고, 키워드 추정과 분류 체계가 어긋나서 대분류 11개로 묶는다 (DEVLOG 2026-10-26).
#
# 규칙은 계속 고치게 된다. 고친 뒤엔 `python -m app.reclassify`로 저장된 공고 전체를 다시 분류한다 (API 호출 없음).

import re

SOURCE_MAIN_CNSTTY = "main_cnstty"
SOURCE_LICENSE = "license"
SOURCE_KEYWORD = "keyword"
SOURCE_NONE = "none"

# 대분류 11개 (화면 순서와 같음)
CATEGORIES = ["건축", "토목", "전기", "통신", "기계설비", "소방", "조경", "산림", "환경", "국가유산", "기타"]

# 1차: 업종 이름에 이 글자가 들어 있으면 그 대분류. 위에서부터 먼저 맞는 것.
# 순서가 의미 있다 ─ "조경식재ㆍ시설물공사업"은 "시설물"보다 "조경"이 먼저 잡혀야 한다.
INDUSTRY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("소방", ("소방",)),
    ("국가유산", ("국가유산",)),
    ("산림", ("산림", "영림")),
    ("조경", ("조경",)),
    ("통신", ("정보통신",)),
    ("전기", ("전기공사업",)),
    ("기계설비", ("기계설비", "가스", "승강기", "산업·환경설비")),
    ("환경", ("환경", "광해", "석면", "상수도관망")),
    ("토목", ("토목", "지반조성", "수중", "철도", "상ㆍ하수도", "지하수")),
    ("건축", ("건축", "창호", "철근", "도장", "구조물해체", "철강구조물")),
]

# 다리 공사("봉두교 시설물 보수공사")는 "보수"가 건축 키워드라 건축으로 새기 쉽다 (사전 검증에서 가장 흔한 오분류).
# "~교" 뒤에 공사 종류가 오면 다리로 본다. 앞 글자가 "학"(학교)이거나 숫자("OO초 외 1교(옥구초)" = 학교 1곳 더)면 제외.
BRIDGE_PATTERN = re.compile(r"(?<![학\d])교(\(|\s*(시설물|보수|보강|재가설|교체|신설|가설|난간|도장))")

# 2차: 공고명 키워드. 구체적인 분야부터 확인하고, 건축처럼 넓은 말은 맨 뒤에 둔다.
# (2026-10-26 사전 검증: 업종이 있는 공고 2,832건을 정답지로 쟀을 때 분류율 85%, 분류한 것 중 정확도 79%)
KEYWORD_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("소방", ("소방", "스프링클러", "화재감지", "소화설비", "자동화재")),
    ("국가유산", ("문화재", "국가유산", "단청", "향교", "서원", "고택", "성곽", "사지")),
    ("산림", ("숲가꾸기", "산림", "임도", "사방", "조림", "병해충", "영림", "숲길", "숲 ", "산불",
             "재선충", "덩굴", "나무가꾸기", "솎아베기", "풀베기", "벌채", "휴양림")),
    ("조경", ("조경", "식재", "수목", "정원", "공원", "놀이터", "화단", "잔디", "전정", "가로수", "녹지")),
    ("통신", ("통신", "CCTV", "cctv", "방송", "네트워크", "전산", "와이파이", "무선", "광케이블")),
    ("전기", ("전기", "조명", "가로등", "보안등", "태양광", "LED", "수배전", "변압기", "전력", "신호등",
             "열선", "UPS", "배터리", "발전기", "피뢰")),
    ("기계설비", ("냉난방", "보일러", "공조", "기계설비", "승강기", "엘리베이터", "가스", "배관", "환기",
               "냉동", "펌프", "급수")),
    ("환경", ("석면", "정화", "오염", "폐기물", "비산먼지")),
    ("토목", ("도로", "포장", "하천", "교량", "배수", "하수", "상수", "관로", "옹벽", "제방", "용수로", "농로",
             "구거", "소하천", "준설", "측구", "침수", "사면", "저수지", "수로", "인도", "보도", "주차장", "터널",
             "정비사업", "기반시설", "세천", "농업기반", "차선", "교통안전", "진입로", "복구", "수해", "용수개발",
             "관정", "차로", "선착장", "부잔교", "방파제", "물양장", "어항", "단지", "도색", "가드레일", "방호",
             "과속방지", "횡단", "지구", "대교", "육교")),
    ("건축", ("건축", "신축", "증축", "리모델링", "개보수", "보수", "방수", "도장", "창호", "지붕", "화장실",
             "외벽", "내부", "인테리어", "청사", "경로당", "회관", "센터", "철거", "해체", "환경개선",
             "시설개선", "교실", "신설", "창고", "샤워실", "쉼터", "관리동", "기숙사", "숙소", "체육관", "강당",
             "도서관", "어린이집", "복지관")),
]


def _first_match(text: str, rules: list[tuple[str, tuple[str, ...]]]) -> str | None:
    for category, words in rules:
        if any(word in text for word in words):
            return category
    return None


def category_of_industry(main_cnstty_nm: str) -> str:
    """업종 이름 → 대분류. 업종은 있는데 어디에도 안 맞으면(축산업, 기타자유업종 등) "기타"."""
    return _first_match(main_cnstty_nm, INDUSTRY_RULES) or "기타"


def category_of_title(bid_ntce_nm: str) -> str | None:
    """공고명 → 대분류 추정. 못 찾으면 None. 다리 공사 패턴을 먼저 본다."""
    if BRIDGE_PATTERN.search(bid_ntce_nm):
        return "토목"
    return _first_match(bid_ntce_nm, KEYWORD_RULES)


def classify(main_cnstty_nm: str | None, lcns_lmt_nm: str | None, bid_ntce_nm: str | None) -> tuple[str | None, str]:
    """
    (category, source)를 돌려준다.
    비유: 신분증(업종)이 있으면 신분증대로, 없으면 출입증(면허 조건)을 보고, 그것도 없으면 옷차림(공고명)을 보고 짐작하고,
    짐작도 안 되면 "모름"이라고 적는다. 짐작한 것과 증명서를 본 것을 구분해 적어 두어야 화면에서 정직하게 표시할 수 있다.
    """
    if main_cnstty_nm:
        return category_of_industry(main_cnstty_nm), SOURCE_MAIN_CNSTTY

    license_category = category_of_industry(lcns_lmt_nm) if lcns_lmt_nm else None
    # 면허가 "기타"(어장정화ㆍ정비업 같은 드문 업종)면 공고명이 더 많은 걸 말해 줄 수 있어서 키워드를 먼저 본다.
    if license_category and license_category != "기타":
        return license_category, SOURCE_LICENSE

    guess = category_of_title(bid_ntce_nm or "")
    if guess:
        return guess, SOURCE_KEYWORD
    if license_category:
        return license_category, SOURCE_LICENSE
    return None, SOURCE_NONE
