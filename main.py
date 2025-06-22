# main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Middleware CORS para permitir llamadas desde frontend externo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción cambia esto a ["https://tudominio.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacenamiento temporal de sesiones en memoria
chat_sessions = {}

class MessageIn(BaseModel):
    session_id: str
    text: str

class MessageOut(BaseModel):
    sender: str  # "user" o "bot"
    text: str

@app.get("/")
def root():
    return {"message": "Middleware FastAPI está activo"}

@app.post("/chat", response_model=List[MessageOut])
def handle_message(msg: MessageIn):
    # Obtener o crear la sesión
    if msg.session_id not in chat_sessions:
        chat_sessions[msg.session_id] = []

    # Guardar el mensaje del usuario
    chat_sessions[msg.session_id].append({
        "sender": "user",
        "text": msg.text
    })

    # Lógica simulada del bot
    user_text = msg.text.lower()
    if "hola" in user_text:
        bot_text = "¡Hola! ¿En qué puedo ayudarte?"
    elif "precio" in user_text:
        bot_text = "Nuestros precios varían según el producto. ¿Qué necesitas?"
    else:
        bot_text = "Lo siento, no entendí eso. ¿Puedes reformular tu pregunta?"

    # Guardar la respuesta del bot
    chat_sessions[msg.session_id].append({
        "sender": "bot",
        "text": bot_text
    })

    return chat_sessions[msg.session_id]

@app.get("/chat/{session_id}", response_model=List[MessageOut])
def get_conversation(session_id: str):
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return chat_sessions[session_id]
