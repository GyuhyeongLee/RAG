# 🧠 AI 문서 기반 챗봇 서비스 (RAG + FastAPI)

## 프로젝트 소개
문서 데이터를 업로드하고, 해당 문서를 기반으로 질문을 하면 답변을 제공하는 **AI 챗봇 서비스**입니다.  
LLM과 RAG(Retrieval-Augmented Generation)를 결합하여 기업 문서, 논문, 매뉴얼 등에 대한 빠르고 정확한 질의응답을 지원합니다.

---

## 주요 기능
✅ 문서 업로드 (멀티파일 지원)  
✅ 문서 기반 질문 응답 (RAG)  
✅ OpenAI GPT-3.5-turbo 기반 답변 제공  
✅ 사용자 인증(JWT) 시스템  
✅ Docker 기반 배포 및 EC2 서버 호스팅  
✅ 확장성 있는 구조 설계

---

## 기술 스택
| 분류 | 기술 |
|------|------|
| 백엔드 | FastAPI, Python |
| LLM | OpenAI GPT-3.5-turbo, LangChain |
| 벡터스토어 | FAISS |
| 인증 | JWT (PyJWT) |
| 배포 | Docker, AWS EC2 |
| 기타 | Git, GitHub, VSCode |

---

## 아키텍처
```plaintext
사용자 → FastAPI 서버 → 문서 업로드 → 벡터스토어 저장 (FAISS)
                      → 질문 요청 → LLM (OpenAI GPT-3.5-turbo) → 답변 반환
```

---

## 기능 설명

### 📂 문서 업로드
- `POST /upload/`  
- `.txt` 파일 업로드 지원  
- 문서를 임베딩 후 벡터스토어에 저장  
- 멀티파일 업로드 가능 (벡터 병합 처리)

### 🤖 문서 기반 챗봇
- `POST /chat/`  
- 업로드한 문서에서 정보를 검색하고 GPT-3.5-turbo로 답변 생성  
- `k` 값 튜닝으로 검색 정확도 조절 가능

### 🔐 사용자 인증
- `POST /signup/` : 회원가입  
- `POST /login/`  : 로그인 및 JWT 발급  
- 추후 토큰 기반 접근 제어 확장 가능

---

## 설치 및 실행 방법

### 1️⃣ 환경 변수 파일 생성
`.env` 파일을 프로젝트 루트에 생성하고 아래 추가
```bash
OPENAI_API_KEY=sk-xxxxxx
```

### 2️⃣ Docker 빌드 및 실행
```bash
docker build --platform linux/amd64 -t fastapi-rag-chatbot .
docker run --platform linux/amd64 -d -p 8000:8000 --env-file .env fastapi-rag-chatbot
```

### 3️⃣ EC2 배포 시
```bash
scp -i <keypair.pem> fastapi-rag-chatbot.tar ubuntu@<ec2-ip>:~/
ssh -i <keypair.pem> ubuntu@<ec2-ip>
docker load -i fastapi-rag-chatbot.tar
docker run --platform linux/amd64 -d -p 8000:8000 --env-file .env fastapi-rag-chatbot
```

---

## 사용 예시
### 문서 업로드
```
POST /upload/
FormData: file = example.txt
```

### 질문
```
POST /chat/
Body:
{
  "question": "문서에서 A에 대해 설명해줘"
}
```

---

## 프로젝트 구조
```
├── app.py                  # FastAPI 서버 메인 로직
├── Dockerfile              # Docker 빌드 설정
├── requirements.txt        # 의존성 패키지 목록
├── .env                    # 환경 변수 (gitignore)
├── database.py             # DB 연결 및 세션
├── models.py               # 유저 테이블 모델
└── auth.py                 # 비밀번호 암호화 및 JWT 처리
```

---

## 향후 개선 사항
- PDF, DOCX 파일 지원 추가  
- ElasticSearch 기반 Hybrid Search 구현  
- 사용자 별 개인화 벡터스토어 관리  
- 관리자 페이지 및 통계 관리 기능 추가  
- HTTPS 적용 및 도메인 연결

---

## 개발자
**AI Engineer 포뇨**  
- GitHub: [GyuhyeongLee](https://github.com/GyuhyeongLee)  
- Email: ingan6951@naver.com  