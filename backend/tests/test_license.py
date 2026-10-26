# 면허제한정보 손질 테스트. 공사만, 공고마다 첫 면허 하나, 코드 떼기.

from app.transformer.license import first_license_by_announcement


def lic(no, grp, sno, name, div="공사", ord_="000"):
    return {"bidNtceNo": no, "bidNtceOrd": ord_, "lmtGrpNo": grp, "lmtSno": sno, "lcnsLmtNm": name, "bsnsDivNm": div}


def test_실제_응답에서_공사_공고마다_첫_면허(real_license_page):
    items = real_license_page["response"]["body"]["items"]

    assert first_license_by_announcement(items) == {
        ("R26BK01779864", "000"): "토목공사업",          # 그룹 1이 그룹 2보다 먼저
        ("R26BK01779808", "000"): "기계설비ㆍ가스공사업",  # "/6202" 코드는 뗀다
    }                                                    # 물품 공고는 빠진다


def test_순번은_숫자로_비교한다():
    # 문자열로 비교하면 "10" < "2"라서 10번째 면허가 뽑힌다
    items = [lic("A1", "1", "10", "열번째/1"), lic("A1", "1", "2", "두번째/2")]

    assert first_license_by_announcement(items) == {("A1", "000"): "두번째"}


def test_차수가_다르면_다른_공고():
    items = [lic("A1", "1", "1", "전기공사업/0036", ord_="000"), lic("A1", "1", "1", "토목공사업/0001", ord_="001")]

    assert first_license_by_announcement(items) == {("A1", "000"): "전기공사업", ("A1", "001"): "토목공사업"}


def test_빈_면허나_용역은_무시():
    items = [lic("A1", "1", "1", ""), lic("A2", "1", "1", "엔지니어링사업/1", div="용역")]

    assert first_license_by_announcement(items) == {}
