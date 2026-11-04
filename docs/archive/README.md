# archive — 옛 문서 보관함

> **지금은 쓰지 않지만 남겨 두는 문서**를 모은 폴더다. 보관만 하고 고치지 않는다.
> 지금 문서는 [CLAUDE.md](../../CLAUDE.md) "문서 지도", 재정비 결정은 [decisions/0001](../decisions/0001-docs-revival.md).

## 개발 일지 — 끝난 단계

마일스톤이 끝나면 그 기간의 [DEVLOG](../DEVLOG.md) 날짜 블록을 여기로 옮긴다. 줄을 그대로 옮기고 머리말만 붙였다.

| 파일 | 단계 | 기간 |
|---|---|---|
| [DEVLOG_M0.md](DEVLOG_M0.md) | 설계 · M0 개발 환경 (옛 머리의 "이 파일을 쓰는 이유", 끝의 작성 예시 포함) | 2026-09-11 ~ 09-12 |
| [DEVLOG_M1.md](DEVLOG_M1.md) | M1 데이터 수집 · 기반 재정비 | 2026-09-12 ~ 10-26 |
| [DEVLOG_M2.md](DEVLOG_M2.md) | M2 정제 · 분석 (사전 검증 규칙 도입 포함) | 2026-10-26 |

옛 DEVLOG의 "작성 규칙" · 카테고리는 [CLAUDE.md](../../CLAUDE.md) "DEVLOG 형식"으로, "환경 요약"은 [ARCHITECTURE](../ARCHITECTURE.md) 6장으로 옮겼다.

## 옛 마일스톤

[MILESTONES.md](MILESTONES.md) — 2026-09-11 계획(간트 포함)과 M0 ~ M2 체크리스트 원본.

| 옛 절 | 지금 |
|---|---|
| 0장 원칙 | [PLAN](../PLAN.md) 2장 |
| 1장 간트 · 일정 | 여기에만 (지난 계획) |
| 2장 M0 ~ M2 | 여기에만, 요약은 PLAN 7장 |
| 2장 M3 ~ M6 | PLAN 4장 (M6의 `troubleshooting.md`는 DEVLOG와 겹쳐 뺌) |
| 3장 진행 현황 | PLAN 3장 |
| 4장 밀릴 때 | PLAN 6장 |
| 5장 커밋 · 세션 · 검증 | [CLAUDE.md](../../CLAUDE.md) |
| 6장 입사 이후 | [REQUIREMENTS](../REQUIREMENTS.md) 6장, 확장 아이디어는 3.6절 |

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
