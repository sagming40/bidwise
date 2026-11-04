# 0001 · docs/를 전역 문서 체계로 재정비

- **상태**: 채택
- **날짜**: 2026-11-04

## 맥락

전역 설정에 "문서 체계" 절이 생겼다. 이 저장소의 문서는 2026-09-11에 코드보다 먼저 쓴 번호 이름 문서 6종(`01_requirements` ~ `06_ui_ux`)과 루트의 `MILESTONES.md` · `DEVLOG.md`다.
그사이 M0 ~ M2가 끝나 공종 분류 · 지역 · 수집 방식이 설계와 달라졌고, 옛 문서는 본문 위에 "→ 2026-10-26 구현:"을 덧붙여 가며 맞춰 왔다. 코드가 아직 없는 API · 화면 설계와 코드가 원본인 컬럼 표 · SQL이 한 문서에 섞여 있어 어디까지 믿을지 읽어 봐야 알 수 있었다.

## 결정

전역의 "손 놓았던 레포를 살릴 때" 순서를 따른다.

- 옛 `docs/` 6개와 `MILESTONES.md`를 `docs/archive/`로 옮기고 고치지 않는다. 옛 이름에서 새 위치를 찾는 표는 `archive/README.md`에 둔다.
- 루트의 `MILESTONES.md` · `DEVLOG.md`는 `docs/PLAN.md` · `docs/DEVLOG.md`로 옮긴다. 기준 모델(cbt-journal)과 PlayLedger가 모두 `docs/` 안에 두고, 루트에 남길 이유가 없다.
- 새 세트 `PLAN` · `DEVLOG` · `REQUIREMENTS` · `ARCHITECTURE` · `DATA_MODEL` · `DESIGN` · `mockups/`는 **지금 코드를 사실로 보고** 쓴다. 옛 문서와 코드가 다르면 코드를 따르고, 코드가 없는 것은 옛 설계를 이어 간다.
- 구현된 컬럼 표 · DDL · 집계 SQL은 뺀다. 원본은 `models.py` · `alembic/versions/` · `bid_repo.py`다.
- **API 명세는 아직 문서가 원본이다.** FastAPI 코드가 없어서 `ARCHITECTURE` 3장으로 옮겨 두고, M3 ~ M5에서 구현한 엔드포인트부터 Swagger로 넘기고 문서에서 뺀다.
- 끝난 M0 ~ M2의 DEVLOG 블록은 `archive/DEVLOG_M{n}.md`로 옮긴다. 줄은 고치지 않는다.
- Figma 목업 5화면을 로컬 HTML `mockups/`로 옮긴다. M3가 바로 다음이라 화면의 기준 그림이 저장소에 있어야 하고, 용어 사전 문구는 Figma에만 있었다.
- DEVLOG의 `[카테고리]` 증상/원인/해결 형식과 커밋 형식은 그 문서 위쪽에 있던 것을 `CLAUDE.md`로 옮겨 계속 쓴다.
- 소급 결정 기록은 지금도 구조를 지배하는 4건(0002 ~ 0005)만 만든다. 나머지 판단은 `DATA_MODEL` 3장과 archive DEVLOG에 있다.

전역 문서 체계와 다르게 두는 것은 없다.

## 검토한 대안

- **제자리에서 이름만 바꾸기 (PlayLedger 방식)** — 코드 주석이 부르는 곳이 12곳뿐이라 절 번호를 지킬 이유가 작고, 설계 시점 문장과 구현 후 덧붙임이 섞인 본문을 그대로 물려받는다.
- **API 명세를 처음부터 빼기** — 구현 전이라 가리킬 원본이 없다.
- **Figma 링크만 남기기** — 지금도 열리지만 저장소 밖 계정에 달려 있고, 전역 기준은 로컬 HTML이다.

## 감수할 것

- archive의 옛 기록은 옛 이름을 그대로 쓴다. `archive/README.md` 대응표로 찾아간다.
- 목업은 Figma를 보고 손으로 다시 그린 것이라 지도 모양 · 일부 숫자가 똑같지 않다. Figma 쪽 지역 묶음과 달리 구현 기준은 16개 지역이다 (`mockups/README.md`).
- 코드 주석만 고치는 커밋이 하나 생긴다. 재정비할 때 회사 PC에 Python · venv가 없어 pytest로 확인하지 못했고, diff가 주석 · docstring뿐인 것만 확인했다.
