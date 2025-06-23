import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del archivo .env

USERNAME = os.getenv("SF_USERNAME")
PASSWORD = os.getenv("SF_PASSWORD")
CLIENT_ID = os.getenv("SF_CLIENT_ID")
CLIENT_SECRET = os.getenv("SF_CLIENT_SECRET")

def authenticate_salesforce():
    url = "https://login.salesforce.com/services/oauth2/token"
    data = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    auth_data = response.json()
    return auth_data["access_token"], auth_data["instance_url"]
def get_open_session(access_token, instance_url, user_name, channel):
    url = f"{instance_url}/services/data/v57.0/query/"
    headers = {"Authorization": f"Bearer {access_token}"}
    soql = f"SELECT Id FROM Chat_Session__c WHERE UserName__c = '{user_name}' AND Channel__c = '{channel}' AND Status__c = 'Abierta' LIMIT 1"
    params = {"q": soql}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    records = response.json().get("records")
    if records:
        return records[0]["Id"]
    return None

def create_chat_session(access_token, instance_url, user_name, channel):
    url = f"{instance_url}/services/data/v57.0/sobjects/Chat_Session__c/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "UserName__c": user_name,
        "Channel__c": channel,
        "Status__c": "Abierta",
        "StartDate__c": datetime.utcnow().isoformat()
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()["id"]

def create_chat_message(access_token, instance_url, session_id, message, direction, sender_name, channel):
    url = f"{instance_url}/services/data/v57.0/sobjects/Chat_Message__c/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "ChatSession__c": session_id,
        "Message__c": message,
        "Direction__c": direction,
        "SenderName__c": sender_name,
        "Channel__c": channel,
        "Timestamp__c": datetime.utcnow().isoformat()
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()["id"]