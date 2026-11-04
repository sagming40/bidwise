# mockups — 화면 목업

> **화면 결정을 그림으로 보여 주는 참고 자료다.** 규격 · 색 · 문구의 단일 출처는 [DESIGN](../DESIGN.md)이고, 프론트엔드가 생기면 구현이 기준이다.
> 원본은 Figma 하이파이 목업이다(2026-09-11). 어느 계정 · 기기에서든 볼 수 있게 2026-11-04 Figma 화면을 보고 HTML로 다시 그려 옮겼다.

- Figma: https://www.figma.com/design/1U0pJWd9aJGnNgIOTz4voD/BidWise-%E2%80%94-UI-Mockup (로그인 없이 보기 가능, 2026-11-04 확인)
- Figma를 고치면 이 폴더도 다시 옮겨야 같아진다

## 보는 방법

- 파일을 브라우저로 그냥 열면(더블클릭) 된다. 빌드 · 서버가 필요 없다. 앱 내장 브라우저에서는 로컬 파일의 스크립트가 돌지 않을 수 있어 로컬 서버로 연다.
- 서체는 Google Fonts에서 받는다. 오프라인이면 맑은 고딕으로 보인다.
- 주소 파라미터:
  - `?state=dashboard|region|empty|glossary` — 상태 바꾸기 (예: `Dashboard.desktop.html?state=empty`)
  - `?term=개찰` — `Glossary.desktop.html`의 팝오버 용어 바꾸기 (용어 8종, [DESIGN](../DESIGN.md) 6장)
- 다크 톤 한 벌이라 다크 전환 파라미터는 없다.

## 파일

| 화면 | 파일 | DESIGN | Figma node | 상태 |
|---|---|---|---|---|
| Screen 1 메인 대시보드 | `Dashboard.desktop.html` | 3장 | `1-19` | **채택** (2026-09-11) |
| Screen 2 지역 선택 → 공고 목록 | `Region.desktop.html` | 4장 | `4-447` | **채택** (2026-09-11) |
| Screen 3 토큰 & 컴포넌트 | `Tokens.html` | 1 · 6 · 7장 | `6-2` | **채택** (2026-09-11) |
| Screen 4 빈 상태 | `Empty.desktop.html` | 5장 | `12-2` | **채택** (2026-09-11) |
| Screen 5 용어 팝오버 | `Glossary.desktop.html` | 6장 | `15-2` | **채택** (2026-09-11) |
| 공용 값 · 부품 | `shared.css` · `shared.js` | | | |

시안 비교는 없었다. Figma에 한 안만 있다.

## DESIGN과 다른 곳 — DESIGN이 기준

Figma를 그대로 옮겼기 때문에 설계가 뒤에 바뀐 부분은 옛 안이다. 다시 그리지 않고 여기에 적어 둔다.

| 목업 | 기준 |
|---|---|
| 지도 · 랭킹의 지역 묶음 (경기·서울·인천, 경남·부산 등) | **16개 지역** (DESIGN 3장). 지도 모양도 실제 GeoJSON이 아니라 대강의 다각형이다 |
| 지도 색 구간이 고른 5단계로 보임 | 실제 범위 · 분위수 구간 (DESIGN 3장) |
| 공종 "전기·통신설비" · "소방설비" · "상하수도" | **대분류 11개** ([0004](../decisions/0004-category-fallback.md)) |
| 막대별 `추정` 배지 | 한 대분류에 추정이 섞인다. 표현은 M4 전에 정한다 (DESIGN 3장) |
| 빈 상태 버튼 "기간 1년으로 넓히기" | "기간 넓혀보기" (DESIGN 5장) |
| 요약 카드 "평균 참가업체" | API에 아직 없다 (ARCHITECTURE 7장) |

숫자와 공고는 Figma에 있던 지어낸 예시 값이다(일부 숫자 · 블루 중간 단계 색은 화면을 보고 옮긴 근사값). 실제 데이터가 아니다.
