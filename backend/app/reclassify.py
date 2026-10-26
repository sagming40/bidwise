# 이 파일의 역할 ─ 저장된 공고를 API 호출 없이 다시 분류하는 스위치
# 지역 정규화·공종 분류 규칙(transformer/region.py, category.py)을 고친 뒤 한 번 돌린다.
# 처음 마이그레이션 0002를 적용한 직후에도 기존 공고의 빈 칸(NULL)을 이걸로 채운다.
#
# 실행 (backend/에서):
#   python -m app.reclassify

import logging
from collections import Counter

from app.database import get_session
from app.repository.bid_repo import CLASSIFICATION_COLUMNS, get_classification_inputs, update_classifications
from app.transformer.announcement import classification_of

logger = logging.getLogger(__name__)


def reclassify() -> dict:
    """
    공고마다 원본(지역명·업종·공고명)에서 정제값을 다시 계산하고, 바뀐 행만 UPDATE한다.
    비유: 도서관 분류표가 바뀌면 책을 새로 사지 않고, 등에 붙은 분류 스티커만 다시 붙인다.
    바뀐 게 없으면 아무것도 쓰지 않으니 몇 번을 돌려도 같다.

    반환값: {"total": 전체 공고 수, "changed": 고친 행 수, "sources": 분류 출처별 개수, "unknown_regions": 지역 못 정한 수}
    """
    with get_session() as session:
        rows = get_classification_inputs(session)

        changes = []
        sources = Counter()
        unknown_regions = 0
        for row in rows:
            new = classification_of(row.cnstrtsite_rgn_nm, row.main_cnstty_nm, row.lcns_lmt_nm, row.bid_ntce_nm)
            sources[new["category_source"]] += 1
            unknown_regions += new["region_normalized"] is None
            if any(getattr(row, col) != new[col] for col in CLASSIFICATION_COLUMNS):
                changes.append({"id": row.id, **new})

        update_classifications(session, changes)
        session.commit()

    result = {"total": len(rows), "changed": len(changes), "sources": dict(sources), "unknown_regions": unknown_regions}
    logger.info("공고 %d건 중 %d건 고침 · 출처 %s · 지역 못 정함 %d건",
                result["total"], result["changed"], result["sources"], result["unknown_regions"])
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    reclassify()
