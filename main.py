# main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import requests
from salesforce import authenticate_salesforce  # importar tu función

app = FastAPI()

# Middleware CORS para permitir llamadas desde frontend externo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacenamiento temporal de sesiones en memoria (opcional)
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
    # --- Autenticar en Salesforce ---
    try:
        access_token, instance_url = authenticate_salesforce()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error autenticando en Salesforce: {str(e)}")

    # --- Preparar payload para Salesforce REST API ---
    payload = {
        "sessionId": msg.session_id,
        "userName": "Cliente desde Middleware",
        "direction": "IN",
        "message": msg.text,
        "senderName": "Cliente",
        "channel": "Web"
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
