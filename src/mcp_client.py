"""Wrapper para conectar con MCP servers (ej: Google Calendar)."""

import asyncio
import os
import threading
from contextlib import AsyncExitStack
from typing import Any, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClientManager:
    """
    Gestiona conexión a un server MCP via stdio.

    Mantiene un event loop dedicado corriendo en un hilo de fondo para que
    la sesión MCP (y sus context managers async) permanezcan vivos entre llamadas.
    """

    def __init__(self, command: str, args: list[str], env: dict | None = None):
        self.command = command
        self.args = args
        self.env = env or {}
        self._loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self._thread: Optional[threading.Thread] = None
        self._session: Optional[ClientSession] = None
        self._exit_stack: Optional[AsyncExitStack] = None
        self._ready = threading.Event()
        self._start_error: Optional[Exception] = None

    def start(self):
        """Arranca el loop en un hilo dedicado e inicializa la sesión MCP."""
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()

        future = asyncio.run_coroutine_threadsafe(self._async_start(), self._loop)
        try:
            future.result(timeout=30)
        except Exception as e:
            raise RuntimeError(f"Error al iniciar servidor MCP: {e}") from e

    async def _async_start(self):
        """Abre el transporte stdio y la sesión, y las deja vivas en el loop."""
        self._exit_stack = AsyncExitStack()
        params = StdioServerParameters(
            command=self.command,
            args=self.args,
            env=self.env,
        )
        stdio, write = await self._exit_stack.enter_async_context(stdio_client(params))
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )
        await self._session.initialize()

    def list_tools(self) -> list:
        """Lista herramientas disponibles en el server."""
        future = asyncio.run_coroutine_threadsafe(
            self._session.list_tools(), self._loop
        )
        return future.result(timeout=30).tools

    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Llama a una herramienta del server y retorna el resultado como string."""
        future = asyncio.run_coroutine_threadsafe(
            self._session.call_tool(name, arguments), self._loop
        )
        result = future.result(timeout=30)
        if result.content:
            return "".join(
                block.text for block in result.content if hasattr(block, "text")
            )
        return "Sin respuesta"

    def close(self):
        """Cierra la sesión y detiene el loop dedicado."""
        if self._exit_stack:
            future = asyncio.run_coroutine_threadsafe(
                self._exit_stack.aclose(), self._loop
            )
            try:
                future.result(timeout=10)
            except Exception:
                pass
        self._loop.call_soon_threadsafe(self._loop.stop)


def get_mcp_client() -> Optional[MCPClientManager]:
    """Crea cliente MCP si está configurado en .env."""
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
            description="Crea un evento en Google Calendar.",
            args_schema=EventInput,
            func=lambda **kwargs: client.call_tool("crear_evento", kwargs),
        ),
        StructuredTool(
            name="listar_eventos_calendario",
            description="Lista los próximos eventos del calendario de Google.",
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
