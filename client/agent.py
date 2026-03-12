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
        self.conversation_history = []

    async def initialize(self) -> None:
        """Load tools and resources from MCP server."""
        # Tools
        mcp_tools = await self.mcp.get_tools()
        self.tools = self.llm.convert_tools(mcp_tools)

        # Resources
        profile_resource = await self.mcp.read_resource("gmail://profile")
        self.profile = profile_resource[0].text if profile_resource else ""

    async def chat(self, user_message: str) -> str:
        # Inject profile context only on first message
        if not self.conversation_history and self.profile:
            context = (
                f"User Gmail profile:\n{self.profile}\n\nUser request: {user_message}"
            )
            self.conversation_history.append({"role": "user", "content": context})
        else:
            self.conversation_history.append({"role": "user", "content": user_message})

        # Call Gemini with history + tools
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


if __name__ == "__main__":

    async def main():
        agent = GmailAgent()
        await agent.initialize()
        print("✅ Profile loaded")
        print(agent.profile)
        print("---")
        response = await agent.chat("list my last 3 emails")
        print(response)

    asyncio.run(main())
