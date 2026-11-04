# 0002 · Python · FastAPI · PostgreSQL · React 스택

- **상태**: 채택 (백엔드 수집 · 정제는 M2까지 구현, FastAPI · 프론트는 M3부터)
- **날짜**: 2026-09-10 (2026-11-04 소급 기록)

## 맥락

공공 API 응답을 모아 집계하고 지도 · 차트로 보여 주는 학습 프로젝트다. 집계 SQL이 핵심이고, 응답 필드가 많다.

## 결정

| 구분 | 기술 | 이유 |
|---|---|---|
| Backend | Python, FastAPI | 공공 API 응답 정제에 Python 생태계가 편하고, Swagger가 따라온다 |
| ORM | SQLAlchemy | 드라이버는 psycopg 3 (0005) |
| DB | PostgreSQL | 집계 · 통계 SQL이 핵심이라 관계형 DB, 그중 집계 함수가 강한 쪽 |
| 스케줄러 | APScheduler | 별도 인프라 없이 앱 안에서 주기 실행 |
| Frontend | React, TypeScript, shadcn/ui | 응답 필드가 많아 타입의 이점이 크고, 대시보드 톤에 맞게 고치기 쉽다 |
| 차트 · 지도 | Recharts, ECharts | 일반 차트는 Recharts, 한국 GeoJSON 코로플레스는 ECharts |

## 검토한 대안

2026-09-10 설계 때 비교 기록을 남기지 않았다. 대안 비교가 필요해지면 새 결정으로 적는다.

## 감수할 것

- 처음 이유에 있던 **pandas는 2026-11-04 현재 `app/`에서 쓰지 않는다.** 정제는 표준 라이브러리로 충분했다. `requirements.txt`에는 APScheduler · FastAPI · uvicorn과 함께 아직 남아 있다(뒤의 셋은 M3 이후에 쓴다).
- 차트 라이브러리가 둘이다. 지도 때문에 ECharts가 필요하지만, 일반 차트까지 합칠지는 M4에서 다시 본다.
