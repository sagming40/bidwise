# 공종 분류 테스트. 1차 업종 → 대분류, 2차 공고명 키워드, 실패 none.

import pytest

from app.transformer.category import CATEGORIES, category_of_industry, category_of_title, classify


@pytest.mark.parametrize("industry, expected", [
    # 2026-10-26 실측 업종 값들
    ("건축공사업", "건축"),
    ("실내건축공사업", "건축"),
    ("금속창호ㆍ지붕건축물조립공사업", "건축"),
    ("전기공사업", "전기"),
    ("토목공사업", "토목"),
    ("지반조성ㆍ포장공사업", "토목"),
    ("상ㆍ하수도설비공사업", "토목"),
    ("기계설비ㆍ가스공사업", "기계설비"),
    ("정보통신공사업", "통신"),
    ("전문소방시설공사업", "소방"),
    ("일반소방시설공사업(전기)", "소방"),  # "전기"보다 "소방"이 먼저
    ("조경식재ㆍ시설물공사업", "조경"),
    ("산림사업법인(숲가꾸기 및 병해충방제)", "산림"),
    ("국유림영림단", "산림"),
    ("종합국가유산수리업(보수단청업)", "국가유산"),
    ("전문국가유산수리업(조경업)", "국가유산"),  # "조경"보다 "국가유산"이 먼저
    ("석면해체.제거업", "환경"),
    ("환경전문공사업(수질분야)", "환경"),
    ("기타자유업종", "기타"),
    ("축산업(가축사육업-돼지)", "기타"),
])
def test_업종을_대분류로_묶는다(industry, expected):
    assert category_of_industry(industry) == expected
    assert expected in CATEGORIES


@pytest.mark.parametrize("title, expected", [
    ("무주 반디나래 지원센터 소방공사", "소방"),
    ("노원구 서울둘레길 조성사업 숲길 정비", "산림"),
    ("2026년 소나무재선충병 방제사업", "산림"),
    ("OO초 운동장 LED 조명 교체", "전기"),
    ("고용노동부 전산랙 패치코드 정비공사", "통신"),
    ("마을안 도로 포장공사", "토목"),
    ("외도수영장 개보수 공사", "건축"),
])
def test_공고명_키워드로_추정한다(title, expected):
    assert category_of_title(title) == expected


@pytest.mark.parametrize("title, expected", [
    ("국도20호선 봉두교 시설물 보수공사", "토목"),        # 다리 보수 → 토목 ("보수"는 건축 키워드지만)
    ("국도36호선 대치천교(상) 등 6개소 시설물 보수공사", "토목"),
    ("대구해서초등학교 옥상방수공사", "건축"),             # 학교는 다리가 아니다
    ("군산서해초 외 1교(옥구초) 지붕보수 및 기타공사", "건축"),  # "외 1교" = 학교 1곳 더
])
def test_다리와_학교를_구분한다(title, expected):
    assert category_of_title(title) == expected


def test_업종이_있으면_업종이_먼저():
    # 공고명은 소방처럼 보여도 업종이 전기면 전기 (공식 분류를 믿는다)
    assert classify("전기공사업", None, "소방 수신기 교체공사") == ("전기", "main_cnstty")


def test_업종이_없으면_키워드():
    assert classify(None, None, "마을안 도로 포장공사") == ("토목", "keyword")


def test_둘_다_안_되면_none():
    assert classify(None, None, "부안군 공고 제2026-1594호") == (None, "none")
    assert classify(None, None, None) == (None, "none")


def test_업종이_없으면_면허가_키워드보다_먼저():
    # 공고명은 토목처럼 보여도 면허가 전기면 전기 (면허는 업종과 96.4% 일치, 키워드는 79%)
    assert classify(None, "전기공사업", "마을안 도로 포장공사") == ("전기", "license")


def test_업종이_있으면_면허보다_업종():
    assert classify("건축공사업", "전기공사업", "청사 신축") == ("건축", "main_cnstty")


def test_면허가_기타면_키워드를_먼저_본다():
    # "어장정화ㆍ정비업"처럼 대분류에 안 맞는 면허는 공고명이 더 많은 걸 말해 준다
    assert classify(None, "어장정화ㆍ정비업", "OO항 방파제 보수공사") == ("토목", "keyword")
    # 공고명으로도 못 정하면 면허의 "기타"라도 쓴다
    assert classify(None, "어장정화ㆍ정비업", "부안군 공고 제2026-1594호") == ("기타", "license")
