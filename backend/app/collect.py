# 이 파일의 역할 ─ "새벽 장보기 한 바퀴"를 손으로 돌리는 스위치
# Collector(가져오기) → Transformer(손질) → Repository(창고에 넣기)를 순서대로 잇기만 한다.
# APScheduler는 M3 이후에 붙인다. 그때도 스케줄러는 이 함수를 부르기만 하면 된다.
#
# 실행 (backend/에서): 기간이 길면 하루씩 나눠서 수집·저장한다
#   python -m app.collect 202610200000 202610202359

import argparse
import logging
from datetime import datetime, timedelta

from sqlalchemy import func, select

from app.collector.client import fetch_all_announcements, fetch_all_results
from app.database import get_session
from app.models import BidAnnouncement, BidResult
from app.repository.bid_repo import upsert_announcements, upsert_results
from app.transformer.announcement import to_announcement_row
from app.transformer.result import pick_final_results, to_result_row

logger = logging.getLogger(__name__)

# 페이지 1장 = 호출 1번. 2026-09-13에 200건씩 받는 것까지 실측으로 확인했다.
NUM_OF_ROWS = 200

# 나라장터 조회 기간 형식 (YYYYMMDDHHMM)
DT_FORMAT = "%Y%m%d%H%M"


def collect(begin_dt: str, end_dt: str) -> dict:
    """
    기간(YYYYMMDDHHMM) 안에 게시된 입찰공고와 그 낙찰결과를 수집해 저장한다.
    순서가 중요하다: 공고를 먼저 넣어야 결과가 붙을 announcement_id가 생긴다.
    한 기간이 통째로 들어가거나 통째로 안 들어간다 (commit은 마지막에 한 번).

    낙찰결과는 개찰이 끝나야 생기므로, 같은 기간을 며칠 뒤 다시 돌리면 새로 나온 결과가 더 붙는다.
    (UPSERT라 두 번 돌려도 행이 중복되지 않는다)
    """
    announcement_items = fetch_all_announcements(begin_dt, end_dt, num_of_rows=NUM_OF_ROWS)
    result_items = fetch_all_results(begin_dt, end_dt, num_of_rows=NUM_OF_ROWS)

    announcement_rows = [to_announcement_row(item) for item in announcement_items]
    result_rows = [to_result_row(item) for item in pick_final_results(result_items)]

    with get_session() as session:
        saved_announcements = upsert_announcements(session, announcement_rows)
        saved_results, skipped_results = upsert_results(session, result_rows)
        session.commit()
        total_announcements = session.scalar(select(func.count()).select_from(BidAnnouncement))
        total_results = session.scalar(select(func.count()).select_from(BidResult))

    logger.info("공고: 받은 %d건 → 저장 %d건, 테이블 전체 %d행",
                len(announcement_items), saved_announcements, total_announcements)
    logger.info("낙찰결과: 받은 %d건 → 최종 %d건 → 저장 %d건 (공고 없어 건너뜀 %d), 테이블 전체 %d행",
                len(result_items), len(result_rows), saved_results, skipped_results, total_results)

    return {
        "announcements": saved_announcements,
        "results": saved_results,
        "results_skipped": skipped_results,
    }


def split_by_day(begin_dt: str, end_dt: str) -> list[tuple[str, str]]:
    """
    긴 기간을 하루 단위 구간으로 자른다. 첫날은 begin_dt부터, 마지막 날은 end_dt까지.
        ("202609300900", "202610021200")
        → [("202609300900", "202609302359"), ("202610010000", "202610012359"), ("202610020000", "202610021200")]
    """
    begin = datetime.strptime(begin_dt, DT_FORMAT)
    end = datetime.strptime(end_dt, DT_FORMAT)

    windows = []
    day_start = begin
    while day_start <= end:
        day_end = min(day_start.replace(hour=23, minute=59), end)
        windows.append((day_start.strftime(DT_FORMAT), day_end.strftime(DT_FORMAT)))
        day_start = (day_start + timedelta(days=1)).replace(hour=0, minute=0)
    return windows


def collect_by_day(begin_dt: str, end_dt: str) -> dict:
    """
    기간을 하루씩 나눠 collect()를 부른다. 하루가 끝날 때마다 commit된다.

    한 달을 한 번에 부르면 (2026-10-26 실측) 공고만 52페이지라 뒤로 갈수록 느려지고,
    48페이지째 시간 초과로 멈추자 그때까지 받은 것이 전부 버려졌다.
    하루씩이면 하루치가 3페이지 남짓이라 빠르고, 실패해도 그날 하루만 다시 돌리면 된다.
    비유: 이삿짐을 트럭 한 대에 다 싣지 않고, 박스 단위로 나르며 하나씩 내려놓는 것.
    """
    totals = {"announcements": 0, "results": 0, "results_skipped": 0}
    for day_begin, day_end in split_by_day(begin_dt, end_dt):
        logger.info("=== %s ~ %s", day_begin, day_end)
        for key, value in collect(day_begin, day_end).items():
            totals[key] += value
    logger.info("전체: 공고 %d건, 낙찰결과 %d건 저장 (공고 없어 건너뜀 %d)",
                totals["announcements"], totals["results"], totals["results_skipped"])
    return totals


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

    parser = argparse.ArgumentParser(description="나라장터 입찰공고·낙찰결과 수동 수집")
    parser.add_argument("begin_dt", help="시작 일시 YYYYMMDDHHMM (예: 202610200000)")
    parser.add_argument("end_dt", help="끝 일시 YYYYMMDDHHMM (예: 202610202359)")
    args = parser.parse_args()

    collect_by_day(args.begin_dt, args.end_dt)
