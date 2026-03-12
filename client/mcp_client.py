import os
import asyncio
from fastmcp import Client

# Path relativo al proyecto — funciona en cualquier máquina
SERVER_PATH = os.path.join(
    os.path.dirname(__file__),  # client/
    "..",  # sube a raíz
    "mcp_server",
    "server.py",
)


class GmailMCPClient:
    def __init__(self, server_path: str = SERVER_PATH):
        self.server_path = os.path.abspath(server_path)

    async def get_system_info(self) -> dict:
        """Get all registered tools, resources, prompts and templates."""
        async with Client(self.server_path) as client:
            tools = await client.list_tools()
            resources = await client.list_resources()
            templates = await client.list_resource_templates()
            prompts = await client.list_prompts()

            return {
                "server": self.server_path,
                "tools": [tool.name for tool in tools],
                "resources": [resource.name for resource in resources],
                "templates": [template.name for template in templates],
                "prompts": [prompt.name for prompt in prompts],
            }


# ─── Solo para probar ─────────────────────────────────────────────────────────
if __name__ == "__main__":

    async def main():
        client = GmailMCPClient()
        info = await client.get_system_info()
        print(info)

    asyncio.run(main())
