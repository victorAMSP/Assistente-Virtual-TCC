import streamlit as st
from datetime import datetime, timedelta

def render_chatbot_view(usuario: str, deps: dict):
    st.title("🤖 Assistente Virtual")

    # ---- Helpers de compatibilidade ----
    def has_uc(name: str) -> bool:
        return deps.get(name) is not None

    # ---- Estados de sessão ----
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "concluidos_via_lembrete" not in st.session_state:
        st.session_state.concluidos_via_lembrete = set()
    if "lembretes_adiados" not in st.session_state:
        st.session_state.lembretes_adiados = {}
    if "ultimo_habito_notificado_id" not in st.session_state:
        st.session_state.ultimo_habito_notificado_id = None

    # ---- Notificador interno ----
    deps["notificador"].verificar_e_notificar(usuario)

    # ---- Lembretes (cards) ----
    habitos_agora = deps["buscar_proximos_uc"].executar(usuario, tolerancia_min=5)
    if habitos_agora:
        st.markdown("### 🔔 Lembretes de Hábitos Próximos")
        for i, h in enumerate(habitos_agora):
            # Guardar o último hábito notificado (para intents sem ID)
            st.session_state.ultimo_habito_notificado_id = h.id

            chave = f"{h.acao}_{str(h.horario)}"
            agora = datetime.now()

            # reagendar_para = st.session_state.lembretes_adiados.get(chave)
            # if reagendar_para and agora < reagendar_para:
            #     continue

            snooze_ate = deps["notificador"].get_snooze_until(chave) if "notificador" in deps else None
            if snooze_ate and agora < snooze_ate:
                continue

            if chave not in st.session_state.concluidos_via_lembrete:
                with st.container():
                    st.info(f"⏰ {h.acao} às {str(h.horario)} ({h.categoria})", icon="🔔")
                    col1, col2 = st.columns(2)
                    # Concluir
                    if col1.button(f"✅ Já concluí [{i}]", key=f"concluir_{i}"):
                        if has_uc("marcar_concluido_uc"):
                            deps["marcar_concluido_uc"].execute(habito_id=h.id, fonte_acao="notificacao")
                        else:
                            deps["registrar_conclusao_uc"].executar(
                                usuario, h.acao, str(h.horario), "sim", h.categoria
                            )

                        st.session_state.concluidos_via_lembrete.add(chave)

                        if "notificador" in deps:
                          deps["notificador"].consumir(chave)

                        st.success(f"Hábito '{h.acao}' marcado como concluído!")

                    # Adiar (snooze)
                    if col2.button(f"🕓 Me lembre depois [{i}]", key=f"adiar_{i}"):
                        # if has_uc("adiar_habito_uc"):
                        #     deps["adiar_habito_uc"].execute(habito_id=h.id, minutos=15)
                        #     st.info("⏳ Lembrete adiado por 15 minutos (salvo no banco).")
                        if has_uc("adiar_lembrete_uc"):
                            deps["adiar_lembrete_uc"].execute(chave=chave, minutos=15)
                            st.info("⏳ Lembrete adiado por 15 minutos.")
                        else:
                            if "notificador" in deps:
                                deps["notificador"].adiar(chave, minutos=15)
                                st.info("⏳ Lembrete adiado por 15 minutos.")                            
                            # st.session_state.lembretes_adiados[chave] = agora + timedelta(minutes=15)
                            # st.info("⏳ Lembrete adiado por 15 minutos.")

    st.markdown("---")
    st.markdown("### 💬 Chat com a Assistente")
    user_input = st.text_input("Digite sua mensagem:", key="user_input")

    if st.button("Enviar"):
        if user_input.strip():
            resposta = ""
            comando = user_input.lower()

            # Comandos explícitos 
            if any(cmd in comando for cmd in ["ver hábitos", "listar hábitos", "quais são meus hábitos", "meus hábitos"]):
                habitos = deps["listar_habitos_uc"].executar(usuario)
                resposta = "📋 Seus hábitos cadastrados:\n" + "\n".join(
                    f"• [ID {h.id}] {h.acao} às {str(h.horario)} ({h.categoria})" for h in habitos
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
                        if has_uc("marcar_concluido_uc"):
                            deps["marcar_concluido_uc"].execute(habito_id=selecionado.id, fonte_acao="chatbot")
                        else:
                            deps["registrar_conclusao_uc"].executar(
                                usuario, selecionado.acao, str(selecionado.horario), "sim", selecionado.categoria
                            )
                        resposta = f"✅ Hábito '{selecionado.acao}' às {str(selecionado.horario)} marcado como CONCLUÍDO."
                    else:
                        resposta = f"⚠️ Hábito ID {habito_id} não encontrado."
                except:
                    resposta = "❌ Comando inválido. Use: marcar como concluído [ID]"

            elif comando in ["gerar relatório", "relatório"]:
                deps["gerar_relatorio_uc"].executar(usuario)
                resposta = "📄 Relatório em PDF gerado com sucesso!"

            else:
                # ---- Integração com NLP ----
                resultados = deps["processador"].processar(user_input)

                for resultado in resultados:
                    acao = resultado.get("acao", "")
                    horario = resultado.get("horario", "")
                    categoria = resultado.get("categoria", "")

                    # INTENT: social
                    if acao == "__social__":
                        saudacoes = ["bom dia", "boa tarde", "boa noite", "olá", "oi", "e aí", "fala comigo"]
                        perguntas = ["qual o próximo hábito", "o que tenho hoje", "hábitos de hoje", "me avisa o que falta"]

                        if categoria in saudacoes:
                            resposta += "👋 Olá! Como posso te ajudar hoje?\n"
                        elif categoria in perguntas:
                            agora = datetime.now()
                            todos = deps["listar_habitos_uc"].executar(usuario)
                            futuros = [
                                h for h in todos
                                if h.horario.to_time() > agora.time()
                            ]
                            if futuros:
                                proximo = sorted(
                                    futuros,
                                    key=lambda x: x.horario.to_seconds()
                                )[0]
                                resposta += f"📌 Seu próximo hábito é '{proximo.acao}' às {str(proximo.horario)} ({proximo.categoria}).\n"
                            else:
                                resposta += "🎉 Você não tem mais hábitos programados para hoje.\n"
                        else:
                            resposta += "🙂 Estou aqui! Pode mandar sua dúvida ou hábito.\n"
                        continue  # próximo resultado

                    # INTENT: concluir
                    if acao == "__concluir__":
                        habito_id = resultado.get("habito_id")
                        alvo_id = habito_id or st.session_state.get("ultimo_habito_notificado_id")

                        if alvo_id is None:
                            resposta += "ℹ️ Diga o ID do hábito para concluir. Ex.: `já concluí 12`.\n"
                            continue

                        if has_uc("marcar_concluido_uc"):
                            ok = deps["marcar_concluido_uc"].execute(habito_id=alvo_id, fonte_acao="chatbot")
                            if ok:
                                resposta += f"✅ Hábito ID {alvo_id} marcado como CONCLUÍDO.\n"
                            else:
                                resposta += f"⚠️ Não consegui concluir o hábito ID {alvo_id}.\n"
                        else:
                            # Fallback: localizar hábito e registrar conclusão 
                            habitos = deps["listar_habitos_uc"].executar(usuario)
                            selecionado = next((h for h in habitos if h.id == alvo_id), None)
                            if selecionado:
                                deps["registrar_conclusao_uc"].executar(
                                    usuario, selecionado.acao, str(selecionado.horario), "sim", selecionado.categoria
                                )
                                resposta += f"✅ Hábito '{selecionado.acao}' às {str(selecionado.horario)} marcado como CONCLUÍDO.\n"
                            else:
                                resposta += f"⚠️ Hábito ID {alvo_id} não encontrado.\n"
                        continue  # próximo resultado

                    # INTENT: adiar (snooze)
                    if acao == "__adiar__":
                        minutos = resultado.get("minutos", 15)
                        habito_id = resultado.get("habito_id")
                        alvo_id = habito_id or st.session_state.get("ultimo_habito_notificado_id")

                        if alvo_id is None:
                            resposta += "ℹ️ Diga o ID do hábito para adiar. Ex.: `adiar 5 em 15 min`.\n"
                            continue

                        if has_uc("adiar_lembrete_uc"):
                            ok = deps["adiar_lembrete_uc"].execute(chave=chave, minutos=int(minutos))
                            if ok:
                                resposta += f"🕓 Lembrete do hábito ID {alvo_id} adiado por {minutos} min.\n"
                            else:
                                resposta += "⚠️ Função de adiar indisponível no momento.\n"
                        else:
                            if "notificador" in deps:
                                deps["notificador"].adiar(chave, minutos=minutos)
                                resposta += f"🕓 Lembrete do hábito ID {alvo_id} adiado por {minutos} min.\n"
                            else:
                                resposta += "⚠️ Função de adiar indisponível no momento.\n"
                        # else:
                        #     habitos = deps["listar_habitos_uc"].executar(usuario)
                        #     alvo = next((h for h in habitos if h.id == alvo_id), None)
                        #     if alvo:
                        #         key = f"{alvo.acao}_{alvo.horario}"
                        #         st.session_state.lembretes_adiados[key] = datetime.now() + timedelta(minutes=int(minutos))
                        #         resposta += f"🕓 Lembrete do hábito '{alvo.acao}' adiado {minutos} min (apenas nesta sessão).\n"
                        #     else:
                        #         resposta += f"⚠️ Hábito ID {alvo_id} não encontrado.\n"
                        continue  # próximo resultado

                    # Cadastro de novos hábitos
                    if not acao or not horario:
                        resposta += "❗ Desculpe, não entendi bem seu pedido. Você pode reformular, incluindo a ação e o horário?\n"
                    else:
                        deps["registrar_habito_uc"].executar(usuario, acao, horario, categoria)
                        resposta += f"✅ Hábito '{acao}' cadastrado para {horario} na categoria {categoria}.\n"

            st.session_state.chat_history.append(("Você", user_input))
            st.session_state.chat_history.append(("Assistente", resposta.strip()))
        else:
            st.warning("Digite algo antes de enviar.")

    # ---- Histórico do chat ----
    for autor, msg in st.session_state.chat_history:
        prefixo = "🧍‍♂️" if autor == "Você" else "🤖"
        st.markdown(f"{prefixo} **{autor}**: {msg}")