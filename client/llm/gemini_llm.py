import os
import asyncio
from google import genai
from google.genai import types
from dotenv import load_dotenv
from client.llm.base import BaseLLM

load_dotenv()


class GeminiLLM(BaseLLM):
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = model

    def convert_tools(self, mcp_tools: list) -> list[types.Tool]:
        """Convert MCP tools to Gemini function declarations format."""
        function_declarations = []

        for tool in mcp_tools:
            properties = {}
            for param_name, param_info in tool.inputSchema.get(
                "properties", {}
            ).items():
                properties[param_name] = types.Schema(
                    type=param_info.get("type", "string").upper(),
                    description=param_info.get("description", ""),
                )

            function_declarations.append(
                types.FunctionDeclaration(
                    name=tool.name,
                    description=tool.description,
                    parameters=types.Schema(
                        type="OBJECT",
                        properties=properties,
                        required=tool.inputSchema.get("required", []),
                    ),
                )
            )

        return [types.Tool(function_declarations=function_declarations)]

    def chat_sync(self, messages: list, tools: list) -> any:
        """Send messages to Gemini with available tools (sync).

        `messages` is a mixed list: plain dicts (user / simple model turns)
        are converted to types.Content; native types.Content objects
        (FunctionCall / FunctionResponse turns) are passed through unchanged.
        """
        gemini_messages = []
        for msg in messages:
            if isinstance(msg, types.Content):
                # Already a native Gemini Content (e.g. FunctionCall or FunctionResponse)
                gemini_messages.append(msg)
            else:
                gemini_messages.append(
                    types.Content(
                        role=msg["role"],
                        parts=[types.Part(text=msg["content"])],
                    )
                )

        return self.client.models.generate_content(
            model=self.model,
            contents=gemini_messages,
            config=types.GenerateContentConfig(tools=tools),
        )

    async def chat(self, messages: list[dict], tools: list) -> any:
        """Async wrapper required by BaseLLM contract."""
        return await asyncio.to_thread(self.chat_sync, messages=messages, tools=tools)

    def extract_tool_calls(self, response) -> list[dict]:
        """Extract tool calls from Gemini response."""
        tool_calls = []

        for part in response.candidates[0].content.parts:
            if part.function_call and part.function_call.name:
                tool_calls.append(
                    {
                        "name": part.function_call.name,
                        "params": dict(part.function_call.args),
                    }
                )

        return tool_calls

    def extract_text(self, response) -> str:
        """Extract plain text from Gemini response."""
        for part in response.candidates[0].content.parts:
            if part.text:
                return part.text
        return ""
