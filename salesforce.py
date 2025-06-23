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
