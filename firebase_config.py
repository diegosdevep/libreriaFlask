import firebase_admin
from firebase_admin import credentials, auth
import pyrebase
import os
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
    cred = credentials.Certificate(os.getenv("FIREBASE_ADMIN_SDK_PATH"))
    firebase_admin.initialize_app(cred)
    print("Firebase Admin inicializado correctamente")
except Exception as e:
    print(f"Error al inicializar Firebase Admin: {e}")