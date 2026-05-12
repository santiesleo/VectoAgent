"""Wrapper para conectar con MCP servers (ej: Google Calendar)."""

import os
import threading
import asyncio
from typing import Any, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClientManager:
    """Gestiona conexion a un server MCP via stdio."""

    def __init__(self, command: str, args: list[str], env: dict | None = None):
        self.command = command
        self.args = args
        self.env = env or {}
        self._exit_stack: Optional[AsyncExitStack] = None
        self._stdio = None
        self._write = None
        self._session: Optional[ClientSession] = None
        self._lock = threading.Lock()

    def start(self):
        """Inicia la conexion al server MCP (thread-safe)."""
        def _run():
            async def _async_start():
                self._exit_stack = AsyncExitStack()
                params = StdioServerParameters(
                    command=self.command,
                    args=self.args,
                    env=self.env,
                )
                stdio_transport = await self._exit_stack.enter_async_context(stdio_client(params))
                self._stdio, self._write = stdio_transport
                self._session = await self._exit_stack.enter_async_context(
                    ClientSession(self._stdio, self._write)
                )
                await self._session.initialize()

            asyncio.run(_async_start())

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        thread.join(timeout=30)
        if not self._session:
            raise RuntimeError("Timeout al iniciar servidor MCP")

    def list_tools(self) -> list:
        """Lista herramientas disponibles en el server."""
        result = asyncio.run(self._session.list_tools())
        return result.tools

    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Llama a una herramienta del server."""
        result = asyncio.run(self._session.call_tool(name, arguments))
        if result.content:
            return "".join(
                block.text for block in result.content if hasattr(block, "text")
            )
        return "Sin respuesta"

    def close(self):
        """Cierra la conexion."""
        if self._exit_stack:
            try:
                asyncio.run(self._exit_stack.aclose())
            except Exception:
                pass


def get_mcp_client() -> Optional[MCPClientManager]:
    """Crea cliente MCP si esta configurado en .env."""
    enabled = os.getenv("MCP_GCAL_ENABLED", "false").lower() == "true"
    if not enabled:
        return None

    cmd = os.getenv("MCP_GCAL_COMMAND", "python")
    args_raw = os.getenv("MCP_GCAL_ARGS", "")
    script_path = os.getenv("MCP_GCAL_SCRIPT", "mcp_google_calendar_server.py")

    args = [a.strip() for a in args_raw.split(",") if a.strip()] + [script_path]
    env = {k: v for k, v in os.environ.items() if k.startswith("GOOGLE_")}

    print(f"[MCP] Conectando a server: {cmd} {args}")
    client = MCPClientManager(command=cmd, args=args, env=env)
    try:
        client.start()
        print("[MCP] Conexion exitosa.")
    except Exception as e:
        print(f"[MCP] Error al conectar: {e}")
        return None

    return client


def get_mcp_tools():
    """Retorna lista de herramientas MCP como LangChain tools."""
    client = get_mcp_client()
    if not client:
        return []

    from langchain_core.tools import StructuredTool
    from pydantic import BaseModel

    class EventInput(BaseModel):
        titulo: str
        descripcion: str = ""
        fecha_inicio: str = ""
        fecha_fin: str = ""
        ubicacion: str = ""

    class ListInput(BaseModel):
        max_results: int = 10

    class DeleteInput(BaseModel):
        event_id: str

    tools = [
        StructuredTool(
            name="crear_evento_calendario",
            description="Crea un evento en Google Calendar. USE SOLO cuando el usuario confirme explicitamente.",
            args_schema=EventInput,
            func=lambda **kwargs: client.call_tool("crear_evento", kwargs),
        ),
        StructuredTool(
            name="listar_eventos_calendario",
            description="Lista los proximos eventos del calendario de Google.",
            args_schema=ListInput,
            func=lambda **kwargs: client.call_tool("listar_eventos", kwargs),
        ),
        StructuredTool(
            name="eliminar_evento_calendario",
            description="Elimina un evento del calendario por su ID.",
            args_schema=DeleteInput,
            func=lambda **kwargs: client.call_tool("eliminar_evento", kwargs),
        ),
    ]

    return tools