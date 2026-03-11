from fastmcp import FastMCP

# Global MCP instance
mcp = FastMCP("Gmail Manager")

# Gmail permission scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]
