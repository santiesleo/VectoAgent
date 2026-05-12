"""MCP Server para Google Calendar con OAuth."""

import os
import sys
import json
from datetime import datetime
from typing import Any

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
TOKEN_FILE = os.getenv("GOOGLE_OAUTH_TOKEN_PATH", "./.secrets/google_token.json")
CLIENT_CONFIG = {
    "installed": {
        "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
        "redirect_uris": ["http://localhost"],
    }
}

mcp = FastMCP("google-calendar")


def get_credentials() -> Credentials:
    """Carga o refresca credenciales OAuth."""
    creds = None
    token_dir = os.path.dirname(TOKEN_FILE)
    if token_dir and not os.path.exists(token_dir):
        os.makedirs(token_dir, exist_ok=True)

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(None)
        else:
            flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
            creds = flow.run_local_server(port=0, prompt="consent")
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return creds


def get_calendar_service():
    """Construye el servicio de Google Calendar."""
    creds = get_credentials()
    return build("calendar", "v3", credentials=creds)


@mcp.tool()
async def crear_evento(
    titulo: str,
    descripcion: str = "",
    fecha_inicio: str = "",
    fecha_fin: str = "",
    ubicacion: str = "",
) -> str:
    """Crea un evento en Google Calendar.

    Args:
        titulo: Titulo del evento (requerido)
        descripcion: Descripcion del evento
        fecha_inicio: Fecha/hora de inicio (ISO 8601 o texto, ej: '2025-06-01T10:00:00')
        fecha_fin: Fecha/hora de fin (ISO 8601 o texto)
        ubicacion: Ubicacion del evento
    """
    try:
        service = get_calendar_service()

        start_iso = fecha_inicio or datetime.now().isoformat()
        end_iso = fecha_fin or datetime.now().isoformat()

        if "T" not in start_iso:
            start_iso += "T10:00:00"
            end_iso += "T11:00:00"

        event = {
            "summary": titulo,
            "description": descripcion,
            "location": ubicacion,
            "start": {"dateTime": start_iso, "timeZone": "America/Bogota"},
            "end": {"dateTime": end_iso, "timeZone": "America/Bogota"},
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()
        return f"Evento creado exitosamente: {created_event.get('htmlLink')}"

    except Exception as e:
        return f"Error al crear evento: {str(e)}"


@mcp.tool()
async def listar_eventos(max_results: int = 10) -> str:
    """Lista proximos eventos del calendario.

    Args:
        max_results: Numero maximo de eventos a listar (default 10)
    """
    try:
        service = get_calendar_service()
        now = datetime.utcnow().isoformat() + "Z"

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])
        if not events:
            return "No hay eventos proximos."

        result = ["Proximos eventos:"]
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            result.append(f"- {event['summary']} ({start})")

        return "\n".join(result)

    except Exception as e:
        return f"Error al listar eventos: {str(e)}"


@mcp.tool()
async def eliminar_evento(event_id: str) -> str:
    """Elimina un evento del calendario por su ID.

    Args:
        event_id: ID del evento a eliminar
    """
    try:
        service = get_calendar_service()
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return "Evento eliminado exitosamente."
    except Exception as e:
        return f"Error al eliminar evento: {str(e)}"


def main():
    print("[MCP Google Calendar Server] Iniciando servidor...", file=sys.stderr, flush=True)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()