import base64
from pathlib import Path

import streamlit as st

from rag import get_query_engine

ASSETS      = Path(__file__).parent / "assets"
LOGO_LIGHT  = str(ASSETS / "clemens5upgrade.png")
LOGO_ENS    = ASSETS / "logo-ens-transparent.png"
def _b64(path): return base64.b64encode(Path(path).read_bytes()).decode()
AVATAR_BOT  = f"data:image/png;base64,{_b64(ASSETS / 'avatar_assistant.png')}"
AVATAR_USER = f"data:image/png;base64,{_b64(ASSETS / 'avatar_user.png')}"

st.set_page_config(page_title="ClemENS", page_icon="🏛️", layout="centered")

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    if LOGO_ENS.exists():
        st.image(str(LOGO_ENS), use_container_width=True)
    st.markdown("---")
    st.markdown("**Chatbot de l'École Normale Supérieure – PSL**")
    st.markdown(
        "Je réponds à vos questions sur les procédures, "
        "documents et informations administratives de l'ENS."
    )
    st.markdown("---")
    st.caption("Propulsé par Mistral AI · RAG · LlamaIndex")

# ── Header ────────────────────────────────────────────────────────────────────

col_logo, col_text = st.columns([1, 5])
with col_logo:
    st.image(LOGO_LIGHT, width=100)
with col_text:
    st.title("ClemENS")
    st.caption("Le chatbot de l'École Normale Supérieure")

# ── RAG engine ────────────────────────────────────────────────────────────────

if "query_engine" not in st.session_state:
    with st.spinner("Chargement du moteur de recherche..."):
        st.session_state.query_engine = get_query_engine()

# ── Chat ──────────────────────────────────────────────────────────────────────

GREETING = (
    "Bonjour ! Moi c'est ClemENS 👋 "
    "Je suis là pour vous aider à naviguer dans la documentation de l'ENS. "
    "Quelle information cherchez-vous ?"
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": GREETING}]

for msg in st.session_state.messages:
    avatar = AVATAR_BOT if msg["role"] == "assistant" else AVATAR_USER
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if prompt := st.chat_input("Posez votre question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=AVATAR_USER):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AVATAR_BOT):
        with st.spinner("Recherche en cours..."):
            response = st.session_state.query_engine.query(prompt)

        answer = str(response)

        sources_md = []
        seen = set()
        for node in response.source_nodes:
            src   = node.metadata.get("source", "")
            title = node.metadata.get("title", "")
            page  = node.metadata.get("page")
            if not src or src in seen:
                continue
            seen.add(src)
            if src.startswith("http"):
                label = title if title else src
                sources_md.append(f"[{label}]({src})")
            else:
                sources_md.append(f"`{src}`" + (f" p.{page}" if page else ""))
        if sources_md:
            answer += "\n\n---\n*Sources : " + " · ".join(sources_md) + "*"

        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
