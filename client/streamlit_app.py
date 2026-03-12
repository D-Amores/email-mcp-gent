import streamlit as st
import asyncio
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.agent import GmailAgent

st.set_page_config(
    page_title="Gmail MCP Assistant",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📬 Gmail Assistant")
st.caption("Gestiona tus correos electrónicos mediante lenguaje natural con IA y MCP.")


@st.cache_resource
def get_agent():
    agent = GmailAgent()
    asyncio.run(agent.initialize())
    return agent


try:
    agent = get_agent()
    info = asyncio.run(agent.mcp.get_system_info())
    connection_ok = True
except Exception as e:
    st.error(f"❌ Error de conexión con el servidor MCP: {str(e)}")
    st.stop()

# ─── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📬 Gmail MCP Agent")
    st.divider()

    # Estado de conexión
    if connection_ok:
        st.success("🟢 Conectado al servidor MCP")
    else:
        st.error("🔴 Desconectado")
    st.divider()

    with st.expander(f"🛠️ Herramientas ({len(info['tools'])})", expanded=True):
        for tool in info["tools"]:
            st.markdown(f"- `{tool}`")

    with st.expander(f"📦 Recursos ({len(info['resources'])})", expanded=False):
        for resource in info["resources"]:
            st.markdown(f"- `{resource}`")

    with st.expander(
        f"🧩 Plantillas ({len(info.get('templates', []))})", expanded=False
    ):
        templates = info.get("templates", [])
        if templates:
            for template in templates:
                st.markdown(f"- `{template}`")
        else:
            st.caption("No hay plantillas disponibles")

    with st.expander(f"💬 Prompts ({len(info['prompts'])})", expanded=False):
        for prompt in info["prompts"]:
            st.markdown(f"- `{prompt}`")

    st.divider()

    st.subheader("⚡ Acciones rápidas")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Resumen diario", use_container_width=True):
            st.session_state.quick_action = "summary"
    with col2:
        if st.button("✍️ Redactar", use_container_width=True):
            st.session_state.quick_action = "compose"

    if st.button("🗑️ Limpiar chat", use_container_width=True):
        st.session_state.messages = []
        agent.conversation_history = []
        st.rerun()

    st.divider()
    st.caption("🔹 FastMCP · Gmail API · Gemini")
    st.caption(f"🕒 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

st.divider()
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🛠️ Herramientas", len(info["tools"]))
with col2:
    st.metric("📦 Recursos", len(info["resources"]))
with col3:
    st.metric("🧩 Plantillas", len(info.get("templates", [])))
with col4:
    st.metric("💬 Prompts", len(info["prompts"]))
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": "¡Hola! Soy tu asistente de Gmail. Puedes preguntarme sobre tus correos, pedirme un resumen diario o ayudarme a redactar mensajes.",
        }
    )

if "quick_action" not in st.session_state:
    st.session_state.quick_action = None

if st.session_state.quick_action == "summary":
    st.session_state.quick_action = None
    with st.spinner("📊 Generando resumen diario..."):
        response = asyncio.run(agent.daily_summary())
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

elif st.session_state.quick_action == "compose":
    st.session_state.quick_action = None
    with st.spinner("✍️ Preparando redactor de correos..."):
        response = asyncio.run(agent.compose_email())
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de chat
if prompt := st.chat_input("💬 Escribe tu mensaje..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Pensando..."):
            response = asyncio.run(agent.chat(prompt))
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
