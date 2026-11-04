# decisions — 결정 기록

> **"왜 이걸로?"에 답하는 결정을 하나에 한 파일로 적는다.** 작은 판단은 DEVLOG `[설계]`에 있다.
> 지난 결정은 고치지 않는다. 뒤집으면 새 파일을 만들고 옛 파일은 상태만 `대체됨 → NNNN`으로 바꾼다.

| 번호 | 결정 | 상태 |
|---|---|---|
| [0001](0001-docs-revival.md) | docs/를 전역 문서 체계로 재정비 | 채택 |
| [0002](0002-stack.md) | Python · FastAPI · PostgreSQL · React 스택 | 채택 |
| [0003](0003-etl-store-first.md) | 미리 수집해 DB에 쌓는다 (ETL) | 채택 |
| [0004](0004-category-fallback.md) | 공종 대분류 11개, 업종 → 면허 → 키워드, 컬럼에 저장 | 채택 |
| [0005](0005-alembic-pinned-versions.md) | Alembic과 버전 고정으로 기기끼리 맞춘다 | 채택 |
