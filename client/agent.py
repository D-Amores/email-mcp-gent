import asyncio
from google.genai import types
from client.mcp_client import GmailMCPClient
from client.llm.gemini_llm import GeminiLLM


class GmailAgent:
    def __init__(self):
        self.mcp = GmailMCPClient()
        self.llm = GeminiLLM()
        self.tools = []
        self.conversation_history = []

    async def initialize(self) -> None:
        """Load and convert MCP tools to Gemini format."""
        mcp_tools = await self.mcp.get_tools()
        self.tools = self.llm.convert_tools(mcp_tools)

    async def chat(self, user_message: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_message})

        # Call Gemini with history + tools
        response = await self.llm.chat(
            messages=self.conversation_history, tools=self.tools
        )

        tool_calls = self.llm.extract_tool_calls(response)

        if tool_calls:
            # 1. Preserve Gemini's own FunctionCall turn as a native Content object.
            #    Gemini requires seeing its own function_call before the function_response.
            self.conversation_history.append(response.candidates[0].content)

            for tool_call in tool_calls:
                tool_result = await self.mcp.call_tool(
                    tool_name=tool_call["name"], params=tool_call["params"]
                )

                # 2. Append the tool result as a native FunctionResponse Content.
                #    role="tool" with Part(function_response=...) is the format
                #    Gemini needs to generate a final text answer.
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

            # 3. Call Gemini again — now it has FunctionCall + FunctionResponse
            #    and will produce the final human-readable text response.
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
        response = await agent.chat(
            "send an email to carlos.amores17@unach.mx"
            "with subject 'Test MCP Agent' "
            "and body 'Hello! This email was sent by my Gmail MCP Agent'"
        )

        print(response)

    asyncio.run(main())
