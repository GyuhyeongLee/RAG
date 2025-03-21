import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from pydantic import BaseModel

from database import SessionLocal
from models import User
from auth import get_password_hash, verify_password, create_access_token

from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# FastAPI 인스턴스 생성
app = FastAPI()

# 전역 벡터스토어
vectorstore = None

# CORS 미들웨어 설정 (개발 단계만 전체 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 모델 정의
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

# DB 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.post("/upload/")
async def upload_file(file: UploadFile):
    global vectorstore
    try:
        # 1. 파일 읽기 및 디코딩
        contents = await file.read()
        string_data = contents.decode("utf-8", errors="ignore")

        # 2. 문서화
        documents = [Document(page_content=string_data, metadata={"source": file.filename})]

        # 3. 문서 분할
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)

        # 4. 임베딩 생성
        embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=OPENAI_API_KEY
        )

        # 5. 기존 벡터스토어가 있으면 추가, 없으면 새로 생성
        if vectorstore is None:
            vectorstore = FAISS.from_documents(docs, embeddings)
            logger.info(f"첫 문서 {file.filename} 업로드 및 벡터스토어 생성 완료")
        else:
            vectorstore.add_documents(docs)
            logger.info(f"{file.filename} 추가 완료! 기존 벡터스토어에 병합")

        return {"message": f"{file.filename} 업로드 및 벡터스토어 업데이트 완료!"}

    except Exception as e:
        logger.error(f"업로드 실패: {e}")
        return {"error": str(e)}

@app.post("/chat/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    global vectorstore
    if vectorstore is None:
        logger.warning("문서가 업로드되지 않음")
        return {"answer": "먼저 문서를 업로드하세요!"}

    qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY),
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )

    answer = qa.run(request.question)

    logger.info(f"질문: {request.question} → 답변: {answer}")
    return {"answer": answer}

@app.post("/signup/")
async def signup(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user:
        raise HTTPException(status_code=400, detail="이미 존재하는 유저입니다.")

    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()

    logger.info(f"회원가입 성공 - 사용자명: {username}")
    return {"message": "회원가입 성공!"}

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="아이디 또는 비밀번호 오류!")

    access_token = create_access_token(data={"sub": user.username})
    logger.info(f"로그인 성공 - 사용자명: {username}")
    return {"access_token": access_token, "token_type": "bearer"}