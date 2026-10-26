# CLAUDE.md

이 저장소에서 일하는 Claude가 지키는 공통 규칙이다.
세션끼리는 기억을 공유하지 않고, 기기도 4대(노트북·집 데스크탑·학교 PC·회사 PC)라서 **저장소가 공용 노트**다. 이 파일과 문서들이 기억 역할을 한다.

BidWise: 나라장터 공사 입찰 데이터를 수집해서 지역별·공종별 낙찰률을 지도와 차트로 보여 주는 대시보드. 학습 프로젝트다.

## 문서 지도 (질문 하나 = 문서 하나)
| 질문 | 문서 |
|---|---|
| 지금 어디까지 왔고 바로 다음에 뭘 해? | [`DEVLOG.md`](DEVLOG.md) "현재 상태" |
| 무엇을 어떤 순서로 만들어? 완료 기준은? | [`MILESTONES.md`](MILESTONES.md) |
| 겪은 문제와 해결, 결정의 근거는? | [`DEVLOG.md`](DEVLOG.md) "기록" (최신이 위) |
| 기능 범위는? | [`docs/01_requirements.md`](docs/01_requirements.md) |
| DB는 어떻게 생겼고 왜? | [`docs/02_erd.md`](docs/02_erd.md) |
| 레이어·디렉터리 구조는? | [`docs/03_architecture.md`](docs/03_architecture.md) (구조는 5장) |
| 조회 API 요청·응답은? | [`docs/04_api_spec.md`](docs/04_api_spec.md) |
| 사용자 흐름은? | [`docs/05_usecase_sequence.md`](docs/05_usecase_sequence.md) |
| 화면은 어떻게 생겼고 왜? | [`docs/06_ui_ux.md`](docs/06_ui_ux.md) |
| 이게 뭐고 어떻게 실행해? | [`README.md`](README.md) |
| 작업할 때 항상 지킬 규칙은? | 이 파일 |

- 같은 내용을 두 곳에 쓰지 않는다. 다른 문서 내용이 필요하면 링크한다
- 설계 문서의 미결정 항목(`- [ ]`)은 지우지 않고 "결정됨 + 근거 + 시점"으로 고친다
- DEVLOG의 지난 기록은 고치지 않고 위에 새 항목을 덧붙인다

## 시작할 때
1. `git pull`
2. [`DEVLOG.md`](DEVLOG.md) "현재 상태"를 읽는다
3. 하려는 일에 맞는 문서를 위 지도에서 골라 본다

## 끝날 때
- DEVLOG "현재 상태"를 고친다 (진행 중 / 다음 작업 / 최근 커밋)
- 겪은 문제·결정은 **그 세션 안에서** DEVLOG에 적는다. 형식과 카테고리는 DEVLOG 위쪽 "작성 규칙"을 따른다
- 끝낸 항목은 MILESTONES 체크박스와 3장 진행 현황 표에 반영한다

## 작업 규칙
- **말투**: 대화 말투는 전역 설정(`~/.claude/CLAUDE.md`)을 따른다. 문서·주석은 지금 문서의 문체를 따른다
- **코드 작성 방식**: 기본은 **자동**이다. Claude가 코드를 직접 쓰고 실행·검증까지 한다
  - 사용자가 "직접 칠게"처럼 원할 때만 **타이핑 학습 모드**로 한다. Claude는 파일에 쓰지 않고, 비유를 곁들인 주석을 단 전체 코드를 보여 주고, 사용자가 친 코드를 검수한다
  - 코드를 쓰는 본격 작업(새 마일스톤 항목, 기능 추가)에 들어가기 전에 "자동으로 할까, 직접 칠래?"를 한 줄로 물어본다. 이미 정해 줬으면 묻지 않는다
- **주석**: 기존 코드처럼 한국어로, "왜 이렇게 했나"와 비유를 곁들인다
- **검증**: 단계마다 눈으로 확인할 증거(psql 결과, 실행 출력, Swagger 응답)를 만들고, 확인한 다음 넘어간다
- **커밋·푸시**: 자동 모드로 작업을 끝내고 검증까지 마쳤으면, 묻지 않고 커밋하고 `git push`까지 한다. 타이핑 학습 모드에서는 사용자가 직접 커밋한다
  - 메시지는 **Summary + Description 구조**로 쓴다 ([`MILESTONES.md`](MILESTONES.md) 5장). Summary는 첫 줄 `feat(M1): ...`, 빈 줄 하나 뒤 Description에 "## 왜 이렇게 했나 / ## 새 파일 / 수정 파일 / ## 겪은 오류와 해결(있을 때만)"을 쓴다
  - 의미 단위로 나눠 커밋한다
  - 검증이 실패했거나 끝나지 않은 작업은 커밋하지 않고 상태를 알린다. `git push --force`, 히스토리 수정은 하지 않는다

## 함정 (고치기 전에 확인)
- **인증키**: `requests`의 `params`로 넘기므로 `.env`에는 `%`가 없는 원본 키를 넣는다. 인코딩된 키(`%3D` 등)는 이중 인코딩되어 인증에 실패한다
- **트래픽 한도**: 서비스별 하루 1,000건, **기기 4대 합산**(인증키 기준). 실제 API 호출은 꼭 필요할 때만, `numOfRows`는 크게. 반복 검증은 저장해 둔 응답 JSON으로
- **공고 유일성**: `bidNtceNo`만으로는 유일하지 않다. 정정공고는 `bidNtceOrd`만 오른다 → `(bid_ntce_no, bid_ntce_ord)` 기준
- **낙찰결과는 0개일 수 있다**: 개찰 전·유찰 공고는 낙찰정보에 행이 없다. 에러로 처리하지 말고, 집계는 `LEFT JOIN`
- **응답의 빈 값**: 결과가 0건이면 `items`가 리스트가 아니라 빈 문자열로 온다. 필드의 `""`는 `None`으로 바꾼다
- **타입**: 금액은 `BIGINT`, 낙찰률은 `NUMERIC(6,3)` (`FLOAT` 금지)
- **PostgreSQL 15+**: 새 DB 유저는 `public` 스키마 CREATE 권한이 없다 → `GRANT ALL ON SCHEMA public TO <유저>;`
- **Claude의 Bash 도구는 외부 API에 못 붙는다** (`apis.data.go.kr` 연결 시간 초과). 실제 API 호출은 PowerShell로 한다
- **한글 출력**: 콘솔에 깨져 보여도 데이터는 정상일 수 있다. 파이썬 출력은 `-X utf8`로 (`-I`는 `PYTHONIOENCODING`을 무시)

## 하지 말 것
- `.env`, API 키를 커밋하지 않는다
- `alembic.ini`에 한글을 쓰지 않는다 (Windows에서 cp949로 읽어서 `UnicodeDecodeError`가 난다). DB 주소도 넣지 않는다 (`alembic/env.py`가 `.env`에서 읽음)
- `backend/scratch/`(버리는 검증 스크립트, gitignore 대상)에 남겨야 할 코드를 두지 않는다. 남길 코드는 `app/`이나 `tests/`로

## 기기 4대
- 코드는 GitHub로 주고받는다 (`git pull` → 작업 → `git push`)
- `.env`와 DB 데이터는 git에 없으므로 기기마다 따로 준비한다 (`.env.example` 참고). 한 기기에서 수집한 데이터는 다른 기기에 없다
- DB 구조는 Alembic으로 맞춘다: `git pull` 후 항상 `alembic upgrade head`
  - `create_tables.py`(2026-10-24 삭제)로 테이블을 만든 기기는 처음 한 번만 `alembic stamp 0001`
  - 마이그레이션 파일은 **models.py를 고친 기기에서만** 만든다. 번호를 붙인다: `alembic revision --autogenerate --rev-id 0002 -m "add something"` → `0002_add_something.py`
  - autogenerate 결과는 그대로 믿지 말고 읽어 본 다음 커밋한다. `pytest`의 마이그레이션 테스트가 모델과 어긋나면 실패한다
- 패키지 버전은 `requirements.txt`에 고정한다. 올리거나 추가했으면 다른 기기에서 `pip install -r requirements.txt` 하라고 DEVLOG에 적는다
- 다른 기기에서 할 일(패키지 설치, 마이그레이션 적용 등)은 DEVLOG "현재 상태"에 적어 둔다

## 자주 쓰는 명령 (`backend/`에서, PowerShell)
```powershell
.\venv\Scripts\Activate.ps1      # 가상환경
pip install -r requirements.txt
alembic upgrade head; alembic check   # 마이그레이션 적용, 모델과 차이 없는지 확인
pytest                           # 테스트 (임시 SQLite·가짜 응답, 실제 DB·API 안 씀)
python -m app.collect 202610200000 202610202359   # 입찰공고 수동 수집 (실제 API 호출 — 한도 주의)
psql -U bidwise_app -d bidwise -c "\dt"   # 테이블 확인
```
