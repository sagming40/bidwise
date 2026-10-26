# 이 파일의 역할 ─ 이미 저장된 공고에 면허제한정보(첫 면허)를 채우고 다시 분류하는 스위치
# 면허제한정보는 2026-10-26에 공종 분류 2차 출처로 추가됐다. 그 전에 수집한 공고는 lcns_lmt_nm이 비어 있어서 한 번 채운다.
# (이후 collect.py로 수집하는 공고는 수집할 때 같이 채워진다)
#
# 실행 (backend/에서): 하루씩 받아서 채우고, 끝나면 재분류까지 한다
#   python -m app.backfill_license 202609260000 202610252359
#
# 호출 수: 하루치가 999건씩 2~3번 (한 달이면 약 60~90번, 입찰공고정보서비스 한도에서 나간다)

import argparse
import logging

from app.collect import split_by_day
from app.collector.client import fetch_all_license_limits
from app.database import get_session
from app.reclassify import reclassify
from app.repository.bid_repo import update_license_names
from app.transformer.license import first_license_by_announcement

logger = logging.getLogger(__name__)


def backfill_licenses(begin_dt: str, end_dt: str) -> int:
    """
    하루씩 면허제한정보를 받아 저장된 공고의 lcns_lmt_nm을 채우고(하루마다 커밋), 마지막에 재분류한다.
    중간에 실패해도 끝난 날까지는 남는다 ─ 실패한 날부터 다시 돌리면 된다 (collect_by_day와 같은 이유).
    반환값: 면허를 채운 공고 수
    """
    filled = 0
    for day_begin, day_end in split_by_day(begin_dt, end_dt):
        licenses = first_license_by_announcement(fetch_all_license_limits(day_begin, day_end))
        with get_session() as session:
            count = update_license_names(session, licenses)
            session.commit()
        filled += count
        logger.info("%s: 공사 공고 면허 %d건 → 저장된 공고에 %d건 채움", day_begin[:8], len(licenses), count)

    logger.info("면허 채운 공고 합계 %d건 → 재분류", filled)
    reclassify()
    return filled


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

    parser = argparse.ArgumentParser(description="저장된 공고에 면허제한정보 채우기 + 재분류")
    parser.add_argument("begin_dt", help="시작 일시 YYYYMMDDHHMM (예: 202609260000)")
    parser.add_argument("end_dt", help="끝 일시 YYYYMMDDHHMM (예: 202610252359)")
    args = parser.parse_args()

    backfill_licenses(args.begin_dt, args.end_dt)
