"""Ejecuta el flujo OAuth de Google Calendar una vez para guardar el token."""

import os
from dotenv import load_dotenv
load_dotenv()

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
TOKEN_FILE = os.getenv("GOOGLE_OAUTH_TOKEN_PATH", "./.secrets/google_token.json")

CLIENT_CONFIG = {
    "installed": {
        "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
        "redirect_uris": ["http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)

print("Abriendo navegador para autorizar Google Calendar...")
flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
creds = flow.run_local_server(port=0, prompt="consent")

with open(TOKEN_FILE, "w") as f:
    f.write(creds.to_json())

print(f"Token guardado en {TOKEN_FILE}")
print("Ya puedes usar la app.")
