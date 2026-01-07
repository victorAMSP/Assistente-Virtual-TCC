import streamlit as st
from startup.main import configurar_dependencias
from presentation.chatbot_view import render_chatbot_view
from presentation.dashboard_view import render_dashboard_view

st.set_page_config(page_title="Assistente Virtual", layout="centered")

# Injetando dependências
deps = configurar_dependencias()

# Usuário fixo para testes
usuario = "usuario_teste"

# Menu lateral
menu = st.sidebar.selectbox("Navegação", ["Chatbot", "Dashboard do Usuário"])

# Roteamento
if menu == "Chatbot":
    render_chatbot_view(usuario, deps)
elif menu == "Dashboard do Usuário":
    render_dashboard_view(usuario, deps)

