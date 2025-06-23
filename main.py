# main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import requests
from salesforce import authenticate_salesforce, get_open_session, create_chat_session, create_chat_message

app = FastAPI()

# Middleware CORS para permitir llamadas desde frontend externo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en producción por el dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacenamiento temporal de sesiones en memoria (opcional)
chat_sessions = {}

class MessageIn(BaseModel):
    session_id: str
    text: str
    user_name: str = "Cliente desde Middleware"  # Por defecto, puedes hacer que lo envíe el cliente
    channel: str = "Web"  # Puedes parametrizar para usar "Messenger" u otro canal

class MessageOut(BaseModel):
    sender: str  # "user" o "bot"
    text: str

@app.get("/")
def root():
    return {"message": "Middleware FastAPI está activo"}

@app.post("/chat", response_model=List[MessageOut])
def handle_message(msg: MessageIn):
    # --- Autenticar en Salesforce ---
    try:
        access_token, instance_url = authenticate_salesforce()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error autenticando en Salesforce: {str(e)}")

    # --- Preparar payload para Salesforce REST API ---
    payload = {
        # sessionId puedes enviarlo o dejar vacío para que Salesforce cree nueva sesión
        "sessionId": msg.session_id if msg.session_id else None,
        "userName": msg.user_name,
        "direction": "IN",  # mensaje entrante (cliente a agente)
        "message": msg.text,
        "senderName": msg.user_name,
        "channel": msg.channel
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # --- Enviar mensaje a Salesforce ---
    try:
        url = f"{instance_url}/services/apexrest/chatWebhook"
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando mensaje a Salesforce: {str(e)}")

    # --- Guardar en memoria local la conversación (opcional) ---
    if msg.session_id not in chat_sessions:
        chat_sessions[msg.session_id] = []

    chat_sessions[msg.session_id].append({
        "sender": "user",
        "text": msg.text
    })
 
    # Respuesta simulada bot (puedes integrar lógica real aquí)
    bot_text = "Mensaje recibido y enviado a Salesforce."

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
