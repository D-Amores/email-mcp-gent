# 📧 Email MCP Agent

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![FastMCP](https://img.shields.io/badge/Server-FastMCP-blueviolet.svg)](https://github.com/jlowin/fastmcp)
[![uv](https://img.shields.io/badge/Runtime-uv-purple.svg)](https://github.com/astral-sh/uv)

An AI-powered agent that seamlessly connects to your Gmail account using the **Model Context Protocol (MCP)**, enabling Large Language Models (LLMs) to read, search, and send emails via natural language instructions.

---

## ✨ Features

- **📧 Read & List Emails**: Retrieve unread messages or fetch recent threads directly from Gmail.
- **✉️ Send Emails**: Compose and dispatch emails effortlessly with automated threading support.
- **🤖 Multi-LLM Support**: Built-in integrations for **Gemini**, **Ollama** (local models), and **DeepSeek**.
- **🔌 Standardized MCP Interface**: Provides tools, resources, and prompts adhering strictly to the Model Context Protocol.
- **🖥️ Streamlit Interface & MCP Client**: Comes with an interactive UI dashboard and a programmatic Python client.

---

## 🧰 MCP Capabilities

This server exposes several Model Context Protocol endpoints to the connected LLMs:

### 🛠️ Tools
Tools allow the model to execute actions on your behalf:
- `list_emails`: Fetches a precise list of your current inbox messages with varied filtering (e.g., unread, categorized).
- `send_email`: Dispatches an email to a chosen recipient with optional subject and body contents.

### 📄 Resources
Resources provide context and read-only data to the model:
- `email_profile`: Returns the active user's Gmail profile information.
- `setup_manual`: Documentation to assist the model with agent execution context.

### 💬 Prompts
Templates for standardized interactions:
- `email_prompts`: Pre-configured instruction templates to help models generate accurate and polite email replies.

---

## 🤖 Supported LLMs
The architecture supports switching smoothly between multiple intelligence engines implemented inside `client/llm/`:
- **Gemini** (`gemini_llm.py`) - Fast and powerful model from Google.
- **Ollama** (`ollama_llm.py`) - Run models completely locally (e.g., `qwen`, `llama3`).
- **DeepSeek** (`deepseek_llm.py`) - High performance LLM via DeepSeek API.

---

## ⚙️ Installation

### 1. Requirements
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (Extremely fast Python package installer and resolver)

### 2. Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/email-mcp-agent
cd email-mcp-agent

# Install dependencies
uv sync

# Install project package
uv pip install -e .
```

### 3. Configuration

Set up environment variables and your Google API credentials.

1. **Variables**: Copy the configuration template and populate it securely.
    ```bash
    cp .env.example .env
    ```
    Configure your `.env` selecting your `LLM_PROVIDER` and adding the resulting API Key:
    ```env
    LLM_PROVIDER=gemini # Options: gemini | ollama | deepseek | openai
    # Add keys for your chosen provider...
    ```

2. **Google Credentials**:
   To authenticate your agent with Gmail API safely, you'll need an OAuth Desktop app credential file.
   - Generate it from the [Google Cloud Console](https://console.cloud.google.com/).
   - Download it and place it on the root of the project with the specific name: `credentials.json`.
   *(During your first run, a browser window will open to authorize the app, which generates a permanent `token.pickle` file).*

---

## 🚀 Usage

### Option A: Run the Streamlit Interface
The most straightforward and visual way to interact with your Email MCP Agent:
```bash
uv run streamlit run client/streamlit_app.py
```

### Option B: Run Programmatically
Start the MCP Server locally independently:
```bash
uv run python mcp_server/server.py
```

Initialize your own workflows with the provided client (`client/mcp_client.py`):
```python
import asyncio
from client.mcp_client import GmailMCPClient

async def run():
    client = GmailMCPClient()
    # Read server registry (tools, resources, prompts)
    system_info = await client.get_system_info()
    print(system_info)

asyncio.run(run())
```

### Option C: Inspecting the MCP Server
FastMCP includes an inspector to map out what your server is currently projecting to its clients.
```bash
fastmcp inspect mcp_server/server.py
```

---

## 📁 Project Structure

```bash
email-mcp-agent/
├── client/
│   ├── llm/                 # Model specific implementations (Gemini, Ollama, DeepSeek)
│   ├── agent.py             # Agent orchestration logic
│   ├── mcp_client.py        # Python MCP Client 
│   └── streamlit_app.py     # UI Dashboard
│
├── mcp_server/
│   ├── tools/               # Action tools (list_emails.py, send_email.py)
│   ├── resources/           # Read-only data (email_profile.py, setup_manual.py)
│   ├── prompts/             # Execution templates (email_prompts.py)
│   ├── config.py            # Server config
│   ├── gmail_auth.py        # OAuth 2.0 flow helper
│   └── server.py            # FastMCP Server Entrypoint
│
├── .env.example             # Environment variables template
├── pyproject.toml           # Project dependencies
└── README.md                # Project documentation
```
