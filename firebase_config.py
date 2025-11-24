import firebase_admin
from firebase_admin import credentials
import pyrebase
import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()

firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "databaseURL": "" 
}

firebase = pyrebase.initialize_app(firebase_config)
auth_client = firebase.auth()

try:
    if os.getenv('FIREBASE_CREDENTIALS'):
        firebase_creds = json.loads(os.getenv('FIREBASE_CREDENTIALS'))
        cred = credentials.Certificate(firebase_creds)
        print("Cargando credenciales desde FIREBASE_CREDENTIALS (JSON directo)")
    
    elif os.getenv('FIREBASE_CREDENTIALS_BASE64'):
        firebase_creds = json.loads(
            base64.b64decode(os.getenv('FIREBASE_CREDENTIALS_BASE64'))
        )
        cred = credentials.Certificate(firebase_creds)
        print("Cargando credenciales desde FIREBASE_CREDENTIALS_BASE64")
    
    elif os.path.exists('serviceAccountKey.json'):
        cred = credentials.Certificate('serviceAccountKey.json')
        print("Cargando credenciales desde archivo local")
    
    else:
        raise ValueError("No se encontró ninguna fuente de credenciales de Firebase")
    
    firebase_admin.initialize_app(cred)
    print("Firebase Admin inicializado correctamente")
    
except Exception as e:
    print(f"Error al inicializar Firebase Admin: {e}")