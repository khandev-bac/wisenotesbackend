from pathlib import Path

import firebase_admin
from firebase_admin import credentials

BASE_DIR = Path(__file__).resolve().parent.parent

cred = credentials.Certificate(
    BASE_DIR / "config" / "config_file" / "wisenotes_backend.json"
)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
