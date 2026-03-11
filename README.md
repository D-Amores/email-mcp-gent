# 📧 Email MCP Agent

AI agent that connects to Gmail using the Model Context Protocol (MCP),
allowing a LLM to read, search and send emails through natural language.

---

## 🛠️ Tech Stack

- **Runtime:** uv
- **MCP Server:** FastMCP
- **LLM:** Anthropic / OpenAI / Ollama
- **Interface:** Streamlit → React + Vite
- **Email:** Gmail API (OAuth 2.0)

---

## ⚙️ Installation

1. Clone the repository
   git clone https://github.com/yourusername/email-mcp-agent
   cd email-mcp-agent

2. Install dependencies
   uv sync

3. Install project package
   uv pip install -e .

4. Set up environment variables
   cp .env.example .env

5. Add your Google credentials
   Place credentials.json in the root of the project

---

## 🚀 Usage

Run the MCP server:
   uv run python mcp_server/server.py

Inspect tools:
   fastmcp inspect mcp_server/server.py

Run the interface:
   uv run streamlit run client/streamlit_app.py

---

## 🧰 MCP Components

| Component | Name | Status |
|---|---|---|
| Tool | `list_emails` | ✅ |
| Tool | `send_email` | 🔄 |
| Tool | `search_emails` | 🔄 |
| Prompt | `reply_email` | 🔄 |
| Resource | `email://templates` | 🔄 |

---

## 🔑 Environment Variables

LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
OLLAMA_BASE_URL=http://localhost:11434
