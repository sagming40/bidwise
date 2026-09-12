import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# .env 파일을 읽어서 환경변수로 load
# 이 함수가 없으면 os.getenv()가 .env 안의 값을 보지 못함.
load_dotenv()

from app.models import Base

# DATABASE_URL 값 꺼내오기. .env에 없으면 None으로 바로 Error가 난 걸 확인할 수 있어야
# 오류를 해결하기 위해 이런저런 시도를 하며 시간을 보내지 않고 무슨 문제인지 바로 알 수 있음.
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError(".env에 DATABASE_URL이 존재하지 않습니다. backend/.env를 확인해보세요.")

# engine = PostgreSQL로 가는 연결선. 실제로 접속하진 않고,
# "이 주소로 접속할 준비가 된 상태"만 미리 만들어둠 (실제 접속은 필요할 때만 ─ 지연 실행)
engine = create_engine(database_url, echo=True)

# Base에 등록된 모든 테이블(BidAnnouncement, BidResult)을 훑어서
# CREATE TABLE로 아직 존재하지 않는 테이블만 생성함. 이미 존재하는 경우 건드리지 않음.
Base.metadata.create_all(engine)

print("🚀 테이블 생성 완료 🚀")
