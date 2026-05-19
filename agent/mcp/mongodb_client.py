import os
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters


def get_mongodb_mcp_toolset(connection_string: str | None = None) -> MCPToolset:
    """
    Returns an ADK MCPToolset backed by the official MongoDB MCP Server.
    The server runs as a local subprocess via npx — no separate process management needed.
    """
    uri = connection_string or os.getenv("MONGODB_URI")
    if not uri:
        raise ValueError("MONGODB_URI must be set (env or argument)")

    return MCPToolset(
        connection_params=StdioServerParameters(
            command="npx",
            args=["-y", "mongodb-mcp-server@latest"],
            env={"MDB_MCP_CONNECTION_STRING": uri},
        )
    )
