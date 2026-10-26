# 이 파일의 역할 ─ "새벽 장보기 한 바퀴"를 손으로 돌리는 스위치
# Collector(가져오기) → Transformer(손질) → Repository(창고에 넣기)를 순서대로 잇기만 한다.
# APScheduler는 M3 이후에 붙인다. 그때도 스케줄러는 이 함수를 부르기만 하면 된다.
#
# 실행 (backend/에서):
#   python -m app.collect 202610200000 202610202359

import argparse
import logging

from sqlalchemy import func, select

from app.collector.client import fetch_all_announcements
from app.database import get_session
from app.models import BidAnnouncement
from app.repository.bid_repo import upsert_announcements
from app.transformer.announcement import to_announcement_row

logger = logging.getLogger(__name__)

# 페이지 1장 = 호출 1번. 2026-09-13에 200건씩 받는 것까지 실측으로 확인했다.
NUM_OF_ROWS = 200


def collect_announcements(begin_dt: str, end_dt: str) -> int:
    """
    기간(YYYYMMDDHHMM) 안의 입찰공고를 수집해 저장하고, 저장한 공고 수를 돌려준다.
    한 기간이 통째로 들어가거나 통째로 안 들어간다 (commit은 마지막에 한 번).
    """
    items = fetch_all_announcements(begin_dt, end_dt, num_of_rows=NUM_OF_ROWS)
    rows = [to_announcement_row(item) for item in items]

    with get_session() as session:
        saved = upsert_announcements(session, rows)
        session.commit()
        total = session.scalar(select(func.count()).select_from(BidAnnouncement))

    logger.info("받은 %d건 → 저장 %d건 (중복 제외), 테이블 전체 %d행", len(items), saved, total)
    return saved


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

    parser = argparse.ArgumentParser(description="나라장터 입찰공고 수동 수집")
    parser.add_argument("begin_dt", help="시작 일시 YYYYMMDDHHMM (예: 202610200000)")
    parser.add_argument("end_dt", help="끝 일시 YYYYMMDDHHMM (예: 202610202359)")
    args = parser.parse_args()

    collect_announcements(args.begin_dt, args.end_dt)
