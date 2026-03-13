import os
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
from client.llm.base import BaseLLM

load_dotenv()


class DeepSeekLLM(BaseLLM):
    def __init__(self, model: str = "deepseek-chat"):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com"
        )
        self.model = model

    def convert_tools(self, mcp_tools: list) -> list:
        """Convert MCP tools to OpenAI/DeepSeek function format."""
        tools = []

        for tool in mcp_tools:
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                param_name: {
                                    "type": param_info.get("type", "string"),
                                    "description": param_info.get("description", ""),
                                }
                                for param_name, param_info in tool.inputSchema.get(
                                    "properties", {}
                                ).items()
                            },
                            "required": tool.inputSchema.get("required", []),
                        },
                    },
                }
            )

        return tools

    def chat_sync(self, messages: list[dict], tools: list) -> any:
        """Send messages to DeepSeek with available tools."""
        deepseek_messages = []
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            entry = {
                "role": msg["role"] if msg["role"] != "model" else "assistant",
                "content": msg.get("content") or "",
            }
            if "tool_calls" in msg:
                entry["tool_calls"] = msg["tool_calls"]
            if "tool_call_id" in msg:
                entry["tool_call_id"] = msg["tool_call_id"]
            if "name" in msg:
                entry["name"] = msg["name"]
            deepseek_messages.append(entry)

        return self.client.chat.completions.create(
            model=self.model,
            messages=deepseek_messages,
            tools=tools if tools else None,
        )

    async def chat(self, messages: list[dict], tools: list) -> any:
        """Async wrapper for DeepSeek chat."""
        return await asyncio.to_thread(self.chat_sync, messages=messages, tools=tools)

    def get_function_call_content(self, response) -> any:
        """DeepSeek needs assistant message with tool_calls in history."""
        message = response.choices[0].message
        return {
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in (message.tool_calls or [])
            ],
        }

    def get_tool_result_content(self, tool_call: dict, tool_result: any) -> any:
        """DeepSeek needs tool message with tool_call_id."""
        return {
            "role": "tool",
            "tool_call_id": tool_call.get("id", ""),
            "name": tool_call["name"],
            "content": str(tool_result),
        }

    def extract_tool_calls(self, response) -> list[dict]:
        """Extract tool calls from DeepSeek response."""
        import json
        tool_calls = []
        try:
            message = response.choices[0].message
            if getattr(message, "tool_calls", None):
                for tc in message.tool_calls:
                    try:
                        params = json.loads(tc.function.arguments)
                    except Exception:
                        params = {}
                    tool_calls.append(
                        {
                            "id": tc.id,
                            "name": tc.function.name,
                            "params": params,
                        }
                    )
        except Exception:
            pass
        return tool_calls

    def extract_text(self, response) -> str:
        """Extract plain text from DeepSeek response."""
        try:
            return response.choices[0].message.content or ""
        except Exception:
            return ""
