# 이 파일의 역할 ─ "재료 손질하는 주방 보조" (낙찰정보 담당)
# 하는 일: API 원본 dict → bid_results 행, 한 공고에 결과가 여럿이면 최종 하나 고르기
# 하지 않는 일: 어느 공고(announcement_id)에 붙일지 찾기 ─ DB를 봐야 하므로 repository 일이다.

from app.transformer.convert import to_date, to_datetime, to_decimal, to_int, to_str


def _key(item: dict) -> tuple[str, str]:
    return item["bidNtceNo"], to_str(item.get("bidNtceOrd")) or "000"


def _order(item: dict) -> tuple[str, str]:
    """
    같은 공고 안에서의 순서. 재입찰번호(rbidNo)가 클수록 나중 개찰이고, 마지막 것이 최종 결과다.
    "000"·"001"처럼 자릿수가 고정된 문자열이라 문자열 비교로 크기를 잴 수 있다.
    """
    return to_str(item.get("rbidNo")) or "000", to_str(item.get("bidClsfcNo")) or "0"


def pick_final_results(items: list[dict]) -> list[dict]:
    """
    한 공고(번호+차수)에 결과 행이 여럿이면 최종 하나만 남긴다.

    낙찰정보 행은 (공고번호, 차수) 말고도 분류번호(bidClsfcNo)·재입찰번호(rbidNo)로 나뉜다.
    유찰 뒤 재입찰하면 rbidNo가 "001"로 오른 행이 따로 생긴다 (2026-10-26 실측 표본에 1건).
    우리 ERD는 공고 1 : 결과 0..1이라(02_erd.md 2장), 재입찰번호가 가장 큰 것 = 최종 결과를 고른다.
    비유: 같은 시험을 재시험 봤으면 성적표는 마지막 시험 것 한 장만 남긴다.
    """
    final: dict[tuple[str, str], dict] = {}
    for item in items:
        key = _key(item)
        if key not in final or _order(item) >= _order(final[key]):
            final[key] = item
    return list(final.values())


def to_result_row(item: dict) -> dict:
    """
    낙찰정보 API 항목 하나 → bid_results 행 하나 (02_erd.md 4.2절).
    announcement_id·id·fetched_at은 repository가 채운다.
    """
    bid_ntce_no, bid_ntce_ord = _key(item)
    return {
        "bid_ntce_no": bid_ntce_no,
        "bid_ntce_ord": bid_ntce_ord,
        "bidwinnr_nm": to_str(item.get("bidwinnrNm")),
        "sucsfbid_amt": to_int(item.get("sucsfbidAmt")),
        # 낙찰률이 빈 문자열로 오는 결과도 있다 (2026-10-26 실측: 72건 중 1건, 참가업체 1곳).
        # None으로 두면 AVG()가 알아서 빼고 평균을 낸다.
        "sucsfbid_rate": to_decimal(item.get("sucsfbidRate")),
        "prtcpt_cnum": to_int(item.get("prtcptCnum")),
        "rl_openg_dt": to_datetime(item.get("rlOpengDt")),
        "fnl_sucsf_date": to_date(item.get("fnlSucsfDate")),
    }
