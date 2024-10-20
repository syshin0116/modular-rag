# Python 3.11 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 설치
RUN pip install poetry

# pyproject.toml과 poetry.lock 복사
COPY pyproject.toml poetry.lock /app/

# 의존성 설치
RUN poetry install --no-root

# 소스 코드 복사
COPY . /app

# FastAPI 서버 실행
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
