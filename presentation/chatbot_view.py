import streamlit as st
from datetime import datetime, timedelta

def render_chatbot_view(usuario: str, deps: dict):
    st.title("🤖 Assistente Virtual")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "concluidos_via_lembrete" not in st.session_state:
        st.session_state.concluidos_via_lembrete = set()

    if "lembretes_adiados" not in st.session_state:
        st.session_state.lembretes_adiados = {}

    # Notificador
    deps["notificador"].verificar_e_notificar(usuario)

    # 🔔 Lembretes
    habitos_agora = deps["buscar_proximos_uc"].executar(usuario, tolerancia_min=5)
    if habitos_agora:
        st.markdown("### 🔔 Lembretes de Hábitos Próximos")
        for i, h in enumerate(habitos_agora):
            chave = f"{h.acao}_{h.horario}"
            agora = datetime.now()

            reagendar_para = st.session_state.lembretes_adiados.get(chave)
            if reagendar_para and agora < reagendar_para:
                continue

            if chave not in st.session_state.concluidos_via_lembrete:
                with st.container():
                    st.info(f"⏰ {h.acao} às {h.horario} ({h.categoria})", icon="🔔")
                    col1, col2 = st.columns(2)
                    if col1.button(f"✅ Já concluí [{i}]", key=f"concluir_{i}"):
                        deps["registrar_conclusao_uc"].executar(usuario, h.acao, h.horario, "sim", h.categoria)
                        st.session_state.concluidos_via_lembrete.add(chave)
                        st.success(f"Hábito '{h.acao}' marcado como concluído!")
                    if col2.button(f"🕓 Me lembre depois [{i}]", key=f"adiar_{i}"):
                        st.session_state.lembretes_adiados[chave] = agora + timedelta(minutes=15)
                        st.info("⏳ Lembrete adiado por 15 minutos.")

    st.markdown("---")
    st.markdown("### 💬 Chat com a Assistente")
    user_input = st.text_input("Digite sua mensagem:", key="user_input")

    if st.button("Enviar"):
        if user_input.strip():
            resposta = ""
            comando = user_input.lower()

            if any(cmd in comando for cmd in ["ver hábitos", "listar hábitos", "quais são meus hábitos", "meus hábitos"]):
                habitos = deps["listar_habitos_uc"].executar(usuario)
                resposta = "📋 Seus hábitos cadastrados:\n" + "\n".join(
                    f"• [ID {h.id}] {h.acao} às {h.horario} ({h.categoria})" for h in habitos
                ) if habitos else "⚠️ Nenhum hábito cadastrado."

            elif comando.startswith("apagar hábito"):
                try:
                    habito_id = int(comando.split()[-1])
                    deps["apagar_habito_uc"].executar(habito_id)
                    resposta = f"🗑️ Hábito com ID {habito_id} foi removido com sucesso."
                except:
                    resposta = "❌ Comando inválido. Tente: apagar hábito [ID]"

            elif comando.startswith("marcar como concluído"):
                try:
                    habito_id = int(comando.split()[-1])
                    habitos = deps["listar_habitos_uc"].executar(usuario)
                    selecionado = next((h for h in habitos if h.id == habito_id), None)
                    if selecionado:
                        deps["registrar_conclusao_uc"].executar(usuario, selecionado.acao, selecionado.horario, "sim", selecionado.categoria)
                        resposta = f"✅ Hábito '{selecionado.acao}' às {selecionado.horario} marcado como CONCLUÍDO."
                    else:
                        resposta = f"⚠️ Hábito ID {habito_id} não encontrado."
                except:
                    resposta = "❌ Comando inválido. Use: marcar como concluído [ID]"

            elif comando in ["gerar relatório", "relatório"]:
                deps["gerar_relatorio_uc"].executar(usuario)
                resposta = "📄 Relatório em PDF gerado com sucesso!"

            else:
                resultados = deps["processador"].processar(user_input)

                for resultado in resultados:
                    acao, horario = resultado["acao"], resultado["horario"]

                    if acao == "__social__":
                        saudacoes = ["bom dia", "boa tarde", "boa noite", "olá", "oi", "e aí", "fala comigo"]
                        perguntas = ["qual o próximo hábito", "o que tenho hoje", "hábitos de hoje", "me avisa o que falta"]

                        if resultado["categoria"] in saudacoes:
                            resposta += "👋 Olá! Como posso te ajudar hoje?\n"
                        elif resultado["categoria"] in perguntas:
                            agora = datetime.now()
                            todos = deps["listar_habitos_uc"].executar(usuario)
                            futuros = [h for h in todos if datetime.strptime(h.horario.replace("h", ":"), "%H:%M").time() > agora.time()]
                            if futuros:
                                proximo = sorted(futuros, key=lambda x: datetime.strptime(x.horario.replace("h", ":"), "%H:%M"))[0]
                                resposta += f"📌 Seu próximo hábito é '{proximo.acao}' às {proximo.horario} ({proximo.categoria}).\n"
                            else:
                                resposta += "🎉 Você não tem mais hábitos programados para hoje.\n"
                        else:
                            resposta += "🙂 Estou aqui! Pode mandar sua dúvida ou hábito.\n"

                    elif not acao or not horario:
                        resposta += "❗ Desculpe, não entendi bem seu pedido. Você pode reformular, incluindo a ação e o horário?\n"
                    else:
                        deps["registrar_habito_uc"].executar(usuario, acao, horario, resultado["categoria"])
                        resposta += f"✅ Hábito '{acao}' cadastrado para {horario} na categoria {resultado['categoria']}.\n"

            st.session_state.chat_history.append(("Você", user_input))
            st.session_state.chat_history.append(("Assistente", resposta.strip()))
        else:
            st.warning("Digite algo antes de enviar.")

    for autor, msg in st.session_state.chat_history:
        prefixo = "🧍‍♂️" if autor == "Você" else "🤖"
        st.markdown(f"{prefixo} **{autor}**: {msg}")