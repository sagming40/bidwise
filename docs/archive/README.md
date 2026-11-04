# archive — 옛 문서 보관함

> **지금은 쓰지 않지만 남겨 두는 문서**를 모은 폴더다. 보관만 하고 고치지 않는다.
> 지금 문서는 [CLAUDE.md](../../CLAUDE.md) "문서 지도", 재정비 결정은 [decisions/0001](../decisions/0001-docs-revival.md).

## 옛 설계 문서 (2026-09-10 ~ 11 작성, 2026-10-26까지 덧붙임)

코드보다 먼저 쓴 설계 문서 6종이다. 옛 기록은 고치지 않으므로 당시 이름이 그대로 남아 있다. 옛 이름에서 지금 위치를 찾을 때 이 표를 본다.

| 옛 파일 | 절 | 지금 |
|---|---|---|
| [01_requirements.md](01_requirements.md) | 1장 개요 · 3 ~ 4장 기능 · 6장 미결정 | [REQUIREMENTS](../REQUIREMENTS.md) 1 · 3 · 5장 |
| | 2장 기술 스택 | [decisions/0002](../decisions/0002-stack.md) |
| | 일정, 5장 개발 순서 | 여기에만 (지난 계획) |
| [02_erd.md](02_erd.md) | 1 · 2장 Entity · 관계 | [DATA_MODEL](../DATA_MODEL.md) 1 · 2장 |
| | 3 · 4장 다이어그램 · 컬럼 표 | `backend/app/models.py` · `alembic/versions/`, API 필드 대응은 `transformer/` |
| | 4장 타입 노트 | DATA_MODEL 3.4절 |
| | 5.1 / 5.2 / 5.3절 | DATA_MODEL 3.1 / 3.2 / 3.3절, 공종은 [decisions/0004](../decisions/0004-category-fallback.md) |
| | 6장 미결정 | DATA_MODEL 4장 |
| | 0장 ERD란 | 여기에만 (용어 설명) |
| [03_architecture.md](03_architecture.md) | 0 · 1장 전체 그림 | [ARCHITECTURE](../ARCHITECTURE.md) 1장 |
| | 2장 왜 미리 쌓는가 | [decisions/0003](../decisions/0003-etl-store-first.md) |
| | 3 · 4장 흐름 | ARCHITECTURE 2장, LEFT JOIN은 DATA_MODEL 2장, SQL은 `bid_repo.py` |
| | 5장 디렉터리 | ARCHITECTURE 4장 (실제 있는 것만) |
| | 6장 엔드포인트 초안 | 04와 겹쳐 여기에만 |
| | 7장 한계 · 8장 미결정 | ARCHITECTURE 5 · 7장 |
| [04_api_spec.md](04_api_spec.md) | 1장 공통 규약 · 5장 네이밍 | ARCHITECTURE 3.0절 |
| | 3.1 ~ 3.6절 | ARCHITECTURE 3.1 ~ 3.6절 (번호 같음, 코드에 맞춰 고침). 근거 SQL은 `bid_repo.py` |
| | 4장 호출 흐름 | ARCHITECTURE 2.4절 |
| | 6장 미결정 | ARCHITECTURE 7장 |
| | 0장 이 문서의 역할 | 여기에만 |
| [05_usecase_sequence.md](05_usecase_sequence.md) | 1 · 2장 Actor · 유즈케이스 | REQUIREMENTS 2장 |
| | 3장 왜 지도인가 | REQUIREMENTS 1장 |
| | 4장 시퀀스 | ARCHITECTURE 2장 |
| | 5장 미결정 | ARCHITECTURE 7장, DESIGN 8장 |
| | 0장, `«include»` 설명 | 여기에만 |
| [06_ui_ux.md](06_ui_ux.md) | 1 ~ 8장 | [DESIGN](../DESIGN.md) 1 ~ 8장 (번호 같음). Figma 링크는 [mockups/README](../mockups/README.md) |
| | 0장 이 문서의 역할 | 여기에만 |
