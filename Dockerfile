FROM python:3.9

# 컨테이너 안에서 작업할 디렉토리 만들기
WORKDIR /app

# requirements 파일 복사 후 패키지 설치
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 소스 전체 복사
COPY . .

# 8000번 포트 열기
EXPOSE 8000

# 서버 실행 명령어
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]