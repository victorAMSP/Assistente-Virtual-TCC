# import streamlit as st
# from infrastructure.repositories.habito_repository_sqlite import HabitoRepositorySQLite
# from infrastructure.repositories.conclusao_repository_sqlite import ConclusaoRepositorySQLite
# from domain.entities.habito import Habito
# from domain.entities.conclusao import Conclusao
# from domain.services.processador_comando_service import ProcessadorComandoService
# from infrastructure.relatorios.gerador_pdf import gerar_pdf
# from datetime import datetime, timedelta, date
# from domain.repositories.habito_repository import IHabitorepository
# from domain.repositories.conclusao_repository import ConclusaoRepository
# from application.use_cases.registrar_habito_usecase import RegistrarHabitoUseCase
# from application.use_cases.listar_habitos_usecase import ListarHabitosComIdUseCase
# from application.use_cases.apagar_habito_por_id import ApagarHabitoPorIdUseCase
# from application.use_cases.registrar_conclusao import RegistrarConclusaoUseCase
# from application.use_cases.listar_conclusoes_usecase import ListarConclusoesUseCase
# from application.use_cases.atualizar_habito_usecase import AtualizarHabitoUseCase
# from application.use_cases.buscar_habitos_proximos_usecase import BuscarHabitosProximosUseCase
# from application.use_cases.gerar_relatorio_pdf_usecase import GerarRelatorioPDFUseCase
# from infrastructure.services.notificacao_service import NotificacaoService

# habito_repo: IHabitorepository = HabitoRepositorySQLite()
# conclusao_repo: ConclusaoRepository = ConclusaoRepositorySQLite()

# st.set_page_config(page_title="Assistente Virtual", layout="centered")

# usuario = "usuario_teste"
# processador = ProcessadorComandoService()
# habito_repo = HabitoRepositorySQLite()
# conclusao_repo = ConclusaoRepositorySQLite()
# gerar_relatorio_uc = GerarRelatorioPDFUseCase(conclusao_repo)
# registrar_habito_uc = RegistrarHabitoUseCase(habito_repo)
# listar_habitos_uc = ListarHabitosComIdUseCase(habito_repo)
# apagar_habito_uc = ApagarHabitoPorIdUseCase(habito_repo)
# registrar_conclusao_uc = RegistrarConclusaoUseCase(conclusao_repo)
# listar_conclusoes_uc = ListarConclusoesUseCase(conclusao_repo)
# atualizar_habito_uc = AtualizarHabitoUseCase(habito_repo)
# buscar_proximos_uc = BuscarHabitosProximosUseCase(habito_repo)
# notificador = NotificacaoService(habito_repo)


# menu = st.sidebar.selectbox("Navegação", ["Chatbot", "Dashboard do Usuário"])

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

# ========================== CHATBOT ==========================

# if menu == "Chatbot":
#     st.title("🤖 Assistente Virtual")

#     notificador.verificar_e_notificar(usuario)

#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []

#     if "concluidos_via_lembrete" not in st.session_state:
#         st.session_state.concluidos_via_lembrete = set()

#     if "lembretes_adiados" not in st.session_state:
#         st.session_state.lembretes_adiados = {}

#     # 🔔 Verificar lembretes no horário atual
#     habitos_agora = buscar_proximos_uc.executar(usuario, tolerancia_min=5)
#     if habitos_agora:
#         st.markdown("### 🔔 Lembretes de Hábitos Próximos")

#         for i, h in enumerate(habitos_agora):
#             chave = f"{h.acao}_{h.horario}"
#             agora = datetime.now()

#             reagendar_para = st.session_state.lembretes_adiados.get(chave)
#             if reagendar_para and agora < reagendar_para:
#                 continue

#             if chave not in st.session_state.concluidos_via_lembrete:
#                 with st.container():
#                     st.info(f"⏰ {h.acao} às {h.horario} ({h.categoria})", icon="🔔")
#                     col1, col2 = st.columns(2)
#                     if col1.button(f"✅ Já concluí [{i}]", key=f"concluir_{i}"):
#                         registrar_conclusao_uc.executar(usuario, h.acao, h.horario, "sim", h.categoria)
#                         st.session_state.concluidos_via_lembrete.add(chave)
#                         st.success(f"Hábito '{h.acao}' marcado como concluído!")
#                     if col2.button(f"🕓 Me lembre depois [{i}]", key=f"adiar_{i}"):
#                         st.session_state.lembretes_adiados[chave] = agora + timedelta(minutes=15)
#                         st.info(f"⏳ Lembrete adiado por 15 minutos.")

#     st.markdown("---")
#     st.markdown("### 💬 Chat com a Assistente")

#     user_input = st.text_input("Digite sua mensagem:", key="user_input")

#     if st.button("Enviar"):
#         if user_input.strip():
#             resposta = ""
#             comando = user_input.lower()

#             if any(cmd in comando for cmd in ["ver hábitos", "listar hábitos", "quais são meus hábitos", "meus hábitos"]):
#                 habitos = listar_habitos_uc.executar(usuario)
#                 if habitos:
#                     resposta = "📋 Seus hábitos cadastrados:\n"
#                     for h in habitos:
#                         resposta += f"• [ID {h.id}] {h.acao} às {h.horario} ({h.categoria})\n"
#                 else:
#                     resposta = "⚠️ Nenhum hábito cadastrado."

#             elif comando.startswith("apagar hábito"):
#                 try:
#                     habito_id = int(comando.split()[-1])
#                     apagar_habito_uc.executar(habito_id)
#                     resposta = f"🗑️ Hábito com ID {habito_id} foi removido com sucesso."
#                 except:
#                     resposta = "❌ Comando inválido. Tente: apagar hábito [ID]"

#             elif comando.startswith("marcar como concluído"):
#                 try:
#                     habito_id = int(comando.split()[-1])
#                     habitos = listar_habitos_uc.executar(usuario)
#                     selecionado = next((h for h in habitos if h.id == habito_id), None)
#                     if selecionado:
#                         registrar_conclusao_uc.executar(usuario, selecionado.acao, selecionado.horario, "sim", selecionado.categoria)
#                         resposta = f"✅ Hábito '{selecionado.acao}' às {selecionado.horario} marcado como CONCLUÍDO."
#                     else:
#                         resposta = f"⚠️ Hábito ID {habito_id} não encontrado."
#                 except:
#                     resposta = "❌ Comando inválido. Use: marcar como concluído [ID]"

#             elif comando in ["gerar relatório", "relatório"]:
#                 gerar_relatorio_uc.executar(usuario)
#                 resposta = "📄 Relatório em PDF gerado com sucesso!"

#             else:
#                 resultado = processador.processar(user_input)
#                 acao, horario = resultado["acao"], resultado["horario"]

#                 if acao == "__social__":
#                     saudacoes = ["bom dia", "boa tarde", "boa noite", "olá", "oi", "e aí", "fala comigo"]
#                     perguntas = ["qual o próximo hábito", "o que tenho hoje", "hábitos de hoje", "me avisa o que falta"]

#                     if resultado["categoria"] in saudacoes:
#                         resposta = "👋 Olá! Como posso te ajudar hoje?"
#                     elif resultado["categoria"] in perguntas:
#                         agora = datetime.now()
#                         todos = listar_habitos_uc.executar(usuario)
#                         futuros = [h for h in todos if datetime.strptime(h.horario.replace("h", ":"), "%H:%M").time() > agora.time()]
#                         if futuros:
#                             proximo = sorted(futuros, key=lambda x: datetime.strptime(x.horario.replace("h", ":"), "%H:%M"))[0]
#                             resposta = f"📌 Seu próximo hábito é '{proximo.acao}' às {proximo.horario} ({proximo.categoria})."
#                         else:
#                             resposta = "🎉 Você não tem mais hábitos programados para hoje."
#                     else:
#                         resposta = "🙂 Estou aqui! Pode mandar sua dúvida ou hábito."

#                 elif not acao or not horario:
#                     resposta = "❗ Desculpe, não entendi bem seu pedido. Você pode reformular, incluindo a ação e o horário?"
#                 else:
#                     registrar_habito_uc.executar(usuario, acao, horario, resultado["categoria"])
#                     resposta = f"✅ Hábito '{acao}' cadastrado para {horario} na categoria {resultado['categoria']}."

#             st.session_state.chat_history.append(("Você", user_input))
#             st.session_state.chat_history.append(("Assistente", resposta))
#         else:
#             st.warning("Digite algo antes de enviar.")

#     for autor, msg in st.session_state.chat_history:
#         if autor == "Você":
#             st.markdown(f"🧍‍♂️ **{autor}**: {msg}")
#         else:
#             st.markdown(f"🤖 **{autor}**: {msg}")

# ====================== DASHBOARD ===========================
# elif menu == "Dashboard do Usuário":
#     st.title("📊 Dashboard do Usuário")
#     st.markdown("Veja seu desempenho com base nos hábitos e conclusões registrados.")

#     st.markdown("### 📅 Calendário de Hábitos")
#     data_escolhida = st.date_input("Selecione um dia para visualizar os hábitos:", date.today())

#     todos_habitos = listar_habitos_uc.executar(usuario)
#     todas_conclusoes = listar_conclusoes_uc.listar(usuario)

#     habitos_concluidos = [c for c in todas_conclusoes if c.data_registro.date() == data_escolhida]
#     habitos_do_dia = []

#     for h in todos_habitos:
#         try:
#             datetime.strptime(h.horario.replace("h", ":"), "%H:%M")
#             habitos_do_dia.append(h)
#         except:
#             continue

#     st.success(f"Hábitos em {data_escolhida.strftime('%d/%m/%Y')}:")
#     if not habitos_do_dia:
#         st.info("Nenhum hábito encontrado para esta data.")
#     else:
#         for h in habitos_do_dia:
#             status = "⏳ Pendente"
#             encontrado = next((c for c in habitos_concluidos if c.acao == h.acao and c.horario == h.horario), None)
#             if encontrado:
#                 status = "✅ Concluído" if encontrado.status == "sim" else "❌ Não realizado"

#             if f"editar_{h.id}" in st.session_state and st.session_state[f"editar_{h.id}"]:
#                 with st.form(f"form_editar_{h.id}"):
#                     nova_acao = st.text_input("Ação:", value=h.acao, key=f"acao_{h.id}")
#                     novo_horario = st.text_input("Horário (ex: 14h00):", value=h.horario, key=f"horario_{h.id}")
#                     nova_categoria = st.text_input("Categoria:", value=h.categoria, key=f"categoria_{h.id}")
#                     colf1, colf2 = st.columns([1, 1])
#                     with colf1:
#                         if st.form_submit_button("💾 Salvar"):
#                             atualizar_habito_uc.executar(h.id, nova_acao, novo_horario, nova_categoria)
#                             st.session_state[f"editar_{h.id}"] = False
#                             st.rerun()
#                     with colf2:
#                         if st.form_submit_button("❌ Cancelar"):
#                             st.session_state[f"editar_{h.id}"] = False
#                             st.rerun()
#             else:
#                 col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
#                 with col1:
#                     st.markdown(f"• **{h.acao}** às {h.horario} — {status} ({h.categoria})")
#                 with col2:
#                     if st.button("📝", key=f"btn_editar_{h.id}", help="Editar"):
#                         st.session_state[f"editar_{h.id}"] = True
#                         st.rerun()
#                 with col3:
#                     if st.button("🗑️", key=f"remover_{h.id}", help="Remover"):
#                         apagar_habito_uc.executar(h.id)
#                         st.rerun()
#                 with col4:
#                     if st.button("✅", key=f"concluir_{h.id}", help="Marcar como concluído"):
#                         registrar_conclusao_uc.executar(usuario, h.acao, h.horario, "sim", h.categoria)
#                         st.rerun()
#                 with col5:
#                     if st.button("❌", key=f"nao_{h.id}", help="Marcar como não realizado"):
#                         registrar_conclusao_uc.executar(usuario, h.acao, h.horario, "não", h.categoria)
#                         st.rerun()

#     # 🎯 Filtros
#     st.markdown("---")
#     st.markdown("### 🎯 Filtros")
#     categorias_disponiveis = ["", "alimentação", "hidratação", "exercício", "sono", "saúde", "bem-estar", "produtividade", "lazer", "geral"]
#     col1, col2 = st.columns(2)
#     with col1:
#         categoria_filtro = st.selectbox("Categoria:", categorias_disponiveis)
#     with col2:
#         data_range = st.date_input("Período:", [])

#     btn_filtrar = st.button("🔍 Aplicar Filtros")

#     if btn_filtrar:
#         data_inicio = data_range[0] if data_range else None
#         data_fim = data_range[1] if len(data_range) == 2 else None

#         resultados = listar_conclusoes_uc.listar_filtrado(
#             usuario=usuario,
#             categoria=categoria_filtro if categoria_filtro else None,
#             data_inicio=data_inicio,
#             data_fim=data_fim
#         )
#     else:
#         resultados = listar_conclusoes_uc.listar(usuario)

#     # 📈 Métricas e Gráficos
#     if resultados:
#         total = len(resultados)
#         concluidos = len([r for r in resultados if r.status == "sim"])
#         nao_concluidos = total - concluidos
#         taxa = (concluidos / total) * 100 if total > 0 else 0

#         colA, colB, colC = st.columns(3)
#         colA.metric("✅ Concluídos", concluidos)
#         colB.metric("❌ Não realizados", nao_concluidos)
#         colC.metric("📊 Taxa de Conclusão", f"{taxa:.1f}%")

#         if taxa >= 80:
#             st.success("🏅 Excelente desempenho! Você está cuidando muito bem dos seus hábitos!")
#         elif taxa >= 50:
#             st.info("💡 Bom trabalho! Continue nesse ritmo e tente melhorar um pouco mais!")
#         else:
#             st.warning("⚠️ Atenção! Que tal focar mais nos seus hábitos nos próximos dias?")

#         from collections import Counter
#         import matplotlib.pyplot as plt

#         # 🥧 Pizza (corrigido)
#         st.markdown("---")
#         st.markdown("### 🥧 Taxa de Conclusão")

#         status_list = [r.status for r in resultados]
#         status_count = Counter(status_list)

#         labels = list(status_count.keys())
#         values = list(status_count.values())

#         if len(values) >= 1:
#             fig1, ax1 = plt.subplots()
#             ax1.pie(
#                 values,
#                 labels=labels,
#                 autopct="%1.1f%%",
#                 startangle=90,
#                 colors=["#00C853", "#FF5252", "#FFC107"][:len(labels)]  # Três cores possíveis
#             )
#             ax1.axis('equal')
#             st.pyplot(fig1)
#         else:
#             st.info("Sem dados suficientes para gerar o gráfico de pizza.")

#         # 📈 Linha
#         st.markdown("---")
#         st.markdown("### 📈 Progresso ao Longo do Tempo")

#         datas = [r.data_registro.date() for r in resultados]
#         progresso_por_data = Counter(datas)
#         datas_ordenadas = sorted(progresso_por_data.items())
#         datas_labels = [d.strftime("%d/%m") for d, _ in datas_ordenadas]
#         valores = [v for _, v in datas_ordenadas]

#         fig_linha, ax_linha = plt.subplots()
#         ax_linha.plot(datas_labels, valores, marker="o", linestyle="-", color="#4CAF50")
#         ax_linha.set_title("Nº de Registros por Dia")
#         ax_linha.set_xlabel("Data")
#         ax_linha.set_ylabel("Total de hábitos registrados")
#         st.pyplot(fig_linha)

#     # 📊 Distribuição por Horário
#     st.markdown("---")
#     st.markdown("### 🕒 Distribuição por Horário")

#     horarios = [r.horario for r in resultados]
#     if horarios:
#         horario_count = Counter(horarios)
#         horario_sorted = dict(sorted(horario_count.items()))
#         fig2, ax2 = plt.subplots()
#         ax2.bar(horario_sorted.keys(), horario_sorted.values(), color="#2196F3")
#         ax2.set_xlabel("Horário")
#         ax2.set_ylabel("Quantidade")
#         ax2.set_title("Frequência de Hábitos por Horário")
#         st.pyplot(fig2)
#     else:
#         st.info("Nenhum dado para exibir no gráfico de horários.")

#         # 📂 Frequência por Categoria
#         st.markdown("---")
#         st.markdown("### 📂 Frequência por Categoria")

#         categorias = [r.categoria for r in resultados if hasattr(r, "categoria")]
#         if categorias:
#             cat_count = Counter(categorias)
#             fig3, ax3 = plt.subplots()
#             ax3.bar(cat_count.keys(), cat_count.values(), color="#FFC107")
#             ax3.set_xlabel("Categoria")
#             ax3.set_ylabel("Quantidade")
#             ax3.set_title("Distribuição por Categoria")
#             st.pyplot(fig3)
#         else:
#             st.info("Nenhum dado para exibir na distribuição por categoria.")