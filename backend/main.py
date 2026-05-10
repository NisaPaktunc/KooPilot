from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import engine, SessionLocal
from models import Base, Product, Message
from services.ai_service import get_ai_response
import uuid

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


@app.get("/")
def home():
    return {"message": "Koopilot backend çalışıyor"}


@app.get("/products")
def get_products():
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        return products
    finally:
        db.close()


@app.post("/chat")
def chat(request: ChatRequest):
    user_message = request.message
    session_id = request.session_id or str(uuid.uuid4())

    # Kullanıcı mesajını veritabanına kaydet
    db = SessionLocal()
    try:
        user_msg = Message(
            session_id=session_id,
            role="user",
            content=user_message
        )
        db.add(user_msg)
        db.commit()
    finally:
        db.close()

    # AI Agent'tan yanıt al
    try:
        ai_result = get_ai_response(user_message)
        response_text = ai_result["response"]
        tools_used = ai_result["tools_used"]
    except Exception as e:
        print(f"❌ AI Service hatası: {e}")
        response_text = f"Üzgünüm, bir hata oluştu. Detay: {str(e)}"
        tools_used = []

    # AI yanıtını veritabanına kaydet
    db = SessionLocal()
    try:
        assistant_msg = Message(
            session_id=session_id,
            role="assistant",
            content=response_text
        )
        db.add(assistant_msg)
        db.commit()
    finally:
        db.close()

    return {
        "response": response_text,
        "session_id": session_id,
        "tools_used": tools_used,
    }


@app.get("/chat/history/{session_id}")
def get_chat_history(session_id: str):
    db = SessionLocal()
    try:
        messages = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.timestamp)
            .all()
        )
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
            }
            for msg in messages
        ]
    finally:
        db.close()
