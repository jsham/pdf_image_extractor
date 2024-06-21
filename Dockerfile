# 베이스 이미지로 Python 3.8 사용
FROM python:3.8-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 복사
COPY requirements.txt requirements.txt
COPY main.py main.py
COPY docs/ docs/

# 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 이미지 디렉토리 생성
RUN mkdir images

# 스크립트 실행
CMD ["python", "main.py"]

