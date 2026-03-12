from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """
    Abstract base class for LLM providers.
    All LLM implementations must follow this contract.
    """

    @abstractmethod
    def convert_tools(self, mcp_tools: list) -> list:
        """
        Convert MCP tools format to the LLM provider's tool format.

        Args:
            mcp_tools: List of tools returned by MCP client

        Returns:
            List of tools in the LLM provider's expected format
        """
        pass

    @abstractmethod
    async def chat(self, messages: list[dict], tools: list) -> dict:
        """
        Send messages to the LLM with available tools.

        Args:
            messages: Conversation history
            tools: Converted tools in LLM provider format

        Returns:
            LLM response with text and/or tool calls
        """
        pass

    @abstractmethod
    def extract_tool_calls(self, response) -> list[dict]:
        """
        Extract tool calls from the LLM response.

        Args:
            response: Raw response from the LLM provider

        Returns:
            List of tool calls with name and parameters
        """
        pass

    @abstractmethod
    def extract_text(self, response) -> str:
        """
        Extract plain text from the LLM response.

        Args:
            response: Raw response from the LLM provider

        Returns:
            Text response from the LLM
        """
        pass
