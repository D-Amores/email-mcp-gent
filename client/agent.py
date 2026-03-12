import asyncio
from google.genai import types
from client.mcp_client import GmailMCPClient
from client.llm.gemini_llm import GeminiLLM


class GmailAgent:
    def __init__(self):
        self.mcp = GmailMCPClient()
        self.llm = GeminiLLM()
        self.tools = []
        self.profile = ""
        self.system_context = ""
        self.summary_prompt = ""
        self.compose_prompt = ""
        self.conversation_history = []

    async def initialize(self) -> None:
        """Load tools, resources and prompts from MCP server."""
        # Tools
        mcp_tools = await self.mcp.get_tools()
        self.tools = self.llm.convert_tools(mcp_tools)

        # Resources
        profile_resource = await self.mcp.read_resource("gmail://profile")
        self.profile = profile_resource[0].text if profile_resource else ""

        self.system_context = f"""
        {self.profile}

        Available resources you can reference:
        - docs://setup-manual/latest  → most recent setup manual
        - docs://setup-manual/v1      → first version
        - docs://setup-manual/v2      → second version
        - docs://setup-manual/v3      → third version
        """

        # Prompts
        summary = await self.mcp.get_prompt("daily_email_summary")
        self.summary_prompt = summary.messages[0].content.text if summary else ""

        compose = await self.mcp.get_prompt("compose_professional_email")
        self.compose_prompt = compose.messages[0].content.text if compose else ""

    async def _get_manual(self, version: str = "latest") -> str:
        """Load setup manual by version on demand."""
        try:
            manual = await self.mcp.read_resource(f"docs://setup-manual/{version}")
            return manual[0].text if manual else ""
        except Exception:
            return ""

    async def _inject_manual_if_needed(self, user_message: str) -> str:
        """Inject manual content if user is asking about it."""
        keywords = ["manual", "setup", "documentation", "guide", "instructions"]
        if any(keyword in user_message.lower() for keyword in keywords):
            version = "latest"
            for v in ["v1", "v2", "v3"]:
                if v in user_message.lower():
                    version = v
                    break
            manual = await self._get_manual(version)
            if manual:
                return f"{user_message}\n\nManual content ({version}):\n{manual}"
        return user_message

    async def chat(self, user_message: str) -> str:
        """Send a message and get a response using Gemini + MCP tools."""
        user_message = await self._inject_manual_if_needed(user_message)

        if not self.conversation_history and self.system_context:
            content = f"{self.system_context}\n\nUser request: {user_message}"
            self.conversation_history.append({"role": "user", "content": content})
        else:
            self.conversation_history.append({"role": "user", "content": user_message})

        response = await self.llm.chat(
            messages=self.conversation_history, tools=self.tools
        )

        tool_calls = self.llm.extract_tool_calls(response)

        if tool_calls:
            self.conversation_history.append(response.candidates[0].content)

            for tool_call in tool_calls:
                tool_result = await self.mcp.call_tool(
                    tool_name=tool_call["name"], params=tool_call["params"]
                )
                self.conversation_history.append(
                    types.Content(
                        role="tool",
                        parts=[
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=tool_call["name"],
                                    response={"result": tool_result},
                                )
                            )
                        ],
                    )
                )

            response = await self.llm.chat(
                messages=self.conversation_history, tools=self.tools
            )

        final_response = self.llm.extract_text(response)
        self.conversation_history.append({"role": "model", "content": final_response})

        return final_response

    async def daily_summary(self) -> str:
        """Activate daily email summary prompt."""
        self.conversation_history = []
        return await self.chat(self.summary_prompt)

    async def compose_email(self, recipient: str = "", subject: str = "") -> str:
        """Activate compose professional email prompt."""
        self.conversation_history = []
        compose = await self.mcp.get_prompt(
            "compose_professional_email", {"recipient": recipient, "subject": subject}
        )
        prompt_text = compose.messages[0].content.text if compose else ""
        return await self.chat(prompt_text)


if __name__ == "__main__":

    async def main():
        agent = GmailAgent()
        await agent.initialize()
        print("✅ Agent initialized")
        print("---")

        # Test daily summary prompt
        summary = await agent.compose_email(
            recipient="carlos.amores17@unach.mx",
            subject="Urge hacer el reporte de actividades que este listo hoy a las 4pm, el ya sabe que actividades y para que se necesita, redacta y envia",
        )
        print("Summary:", summary)

    asyncio.run(main())
