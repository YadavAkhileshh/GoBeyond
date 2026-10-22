import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv(override=True)

TAVILY_API_KEY      = os.getenv("TAVILY_API_KEY", "")
AVIATION_API_KEY    = os.getenv("AVIATION_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

_PROJECT_DIR = Path(__file__).resolve().parent

_DEFAULT_PYTHON = str(_PROJECT_DIR / "langgraph_env" / "Scripts" / "python.exe")
if not Path(_DEFAULT_PYTHON).exists():
    _DEFAULT_PYTHON = sys.executable

AVIATION_MCP_PYTHON = os.getenv(
    "AVIATION_MCP_PYTHON",
    str(_PROJECT_DIR / "aviationstack-mcp" / ".venv" / "Scripts" / "python.exe"),
)
WEATHER_MCP_PYTHON = os.getenv("WEATHER_MCP_PYTHON", _DEFAULT_PYTHON)
WEATHER_MCP_SCRIPT = os.getenv(
    "WEATHER_MCP_SCRIPT",
    str(_PROJECT_DIR / "mcp_weather_server.py"),
)

_server_config: dict = {
    "tavily": {
        "transport": "streamable_http",
        "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
    },
}

if Path(AVIATION_MCP_PYTHON).exists():
    _server_config["aviationstack"] = {
        "transport": "stdio",
        "command": AVIATION_MCP_PYTHON,
        "args": ["-m", "aviationstack_mcp", "mcp", "run"],
        "env": {"AVIATION_STACK_API_KEY": AVIATION_API_KEY},
    }
else:
    print(f"[mcp] AviationStack not found at {AVIATION_MCP_PYTHON}", file=sys.stderr)

if Path(WEATHER_MCP_SCRIPT).exists():
    _server_config["weather"] = {
        "transport": "stdio",
        "command": WEATHER_MCP_PYTHON,
        "args": [WEATHER_MCP_SCRIPT],
        "env": {"OPENWEATHER_API_KEY": OPENWEATHER_API_KEY},
    }
else:
    print(f"[mcp] Weather script not found at {WEATHER_MCP_SCRIPT}", file=sys.stderr)

client = MultiServerMCPClient(_server_config)

_tools_cache: list | None = None


async def get_tools() -> list:
    global _tools_cache
    if _tools_cache is None:
        _tools_cache = await client.get_tools()
    return _tools_cache


async def call_tool(tool_name: str, args: dict | None = None):
    tools = await get_tools()
    tool = next((t for t in tools if t.name == tool_name), None)
    if tool is None:
        return f"[{tool_name} not available]"
    return await tool.ainvoke(args or {})


async def tavily_search(query: str):
    return await call_tool("tavily_search", {"query": query})


async def list_airports(search: str = "", limit: int = 10):
    return await call_tool("list_airports", {"search": search, "limit": limit, "offset": 0})


async def list_airlines(search: str = "", limit: int = 10):
    return await call_tool("list_airlines", {"search": search, "limit": limit, "offset": 0})


async def current_weather(city: str):
    return await call_tool("get_current_weather", {"city": city})


async def forecast(city: str):
    return await call_tool("get_forecast", {"city": city})
