import asyncio
import ollama
from client.llm.base import BaseLLM


class OllamaLLM(BaseLLM):
    def __init__(self, model: str = "qwen3.5:9b"):
        self.client = ollama.Client()
        self.model = model

    def convert_tools(self, mcp_tools: list) -> list:
        """Convert MCP tools to Ollama function format."""
        ollama_tools = []

        for tool in mcp_tools:
            ollama_tools.append(
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

        return ollama_tools

    def chat_sync(self, messages: list[dict], tools: list) -> any:
        """Send messages to Ollama with available tools."""
        ollama_messages = []
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            entry = {
                "role": "assistant" if msg["role"] == "model" else msg["role"],
                "content": msg.get("content") or "",
            }
            # Preserve tool_calls so Ollama can correlate tool results
            if "tool_calls" in msg:
                entry["tool_calls"] = msg["tool_calls"]
            ollama_messages.append(entry)

        return self.client.chat(
            model=self.model,
            messages=ollama_messages,
            tools=tools if tools else None,
        )

    async def chat(self, messages: list[dict], tools: list) -> any:
        """Async wrapper for Ollama chat."""
        return await asyncio.to_thread(self.chat_sync, messages=messages, tools=tools)

    def extract_tool_calls(self, response) -> list[dict]:
        """Extract tool calls from Ollama response."""
        tool_calls = []

        message = response.message
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_calls.append(
                    {
                        "name": tool_call.function.name,
                        "params": dict(tool_call.function.arguments),
                    }
                )

        return tool_calls

    def extract_text(self, response) -> str:
        """Extract plain text from Ollama response."""
        return response.message.content or ""

    def get_function_call_content(self, response) -> any:
        """Ollama needs the assistant message WITH tool_calls preserved in history."""
        entry = {
            "role": "assistant",
            "content": response.message.content or "",
        }
        # Preserve tool_calls so Ollama knows what it called when we send the result
        if response.message.tool_calls:
            entry["tool_calls"] = [
                {
                    "function": {
                        "name": tc.function.name,
                        "arguments": dict(tc.function.arguments),
                    }
                }
                for tc in response.message.tool_calls
            ]
        return entry

    def get_tool_result_content(self, tool_name: str, tool_result: any) -> any:
        """Ollama needs a tool message dict."""
        return {
            "role": "tool",
            "content": str(tool_result),
        }
