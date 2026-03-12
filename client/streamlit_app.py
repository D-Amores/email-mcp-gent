import streamlit as st
from mcp_client import GmailMCPClient
import asyncio

st.set_page_config(
    page_title="Gmail MCP Agent",
    page_icon="✉️",
    layout="wide",
)


# ─── Client ───────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return GmailMCPClient()


client = get_client()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("✉️ Gmail MCP Agent")
    st.divider()

    with st.spinner("Connecting to MCP server..."):
        info = asyncio.run(client.get_system_info())

    st.success("MCP Server connected")
    st.divider()

    with st.expander(f"🔧 Tools ({len(info['tools'])})", expanded=True):
        for tool in info["tools"]:
            st.markdown(f"- `{tool}`")

    with st.expander(f"📦 Resources ({len(info['resources'])})", expanded=False):
        for resource in info["resources"]:
            st.markdown(f"- `{resource}`")

    with st.expander(
        f"🧩 Templates ({len(info.get('templates', []))})", expanded=False
    ):
        if info.get("templates"):
            for template in info["templates"]:
                st.markdown(f"- `{template}`")
        else:
            st.caption("No templates available")

    with st.expander(f"💬 Prompts ({len(info['prompts'])})", expanded=False):
        for prompt in info["prompts"]:
            st.markdown(f"- `{prompt}`")

    st.divider()
    st.caption("Powered by FastMCP · Gmail API")

# ─── Main ─────────────────────────────────────────────────────────────────────
st.title("📬 Gmail Assistant")
st.caption("Manage your emails through natural language using AI and MCP.")
st.divider()

col1, col2, col3, col4 = st.columns(4)
col1.metric("🔧 Tools", len(info["tools"]))
col2.metric("📦 Resources", len(info["resources"]))
col3.metric("🧩 Templates", len(info.get("templates", [])))
col4.metric("💬 Prompts", len(info["prompts"]))
