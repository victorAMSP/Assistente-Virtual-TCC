import streamlit as st
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime, date

def render_dashboard_view(usuario: str, deps: dict):
    st.title("📊 Dashboard do Usuário")
    st.markdown("Veja seu desempenho com base nos hábitos e conclusões registrados.")

    def has_uc(name: str) -> bool:
        return isinstance(deps.get(name), object)

    st.markdown("### 📅 Calendário de Hábitos")
    data_escolhida = st.date_input("Selecione um dia para visualizar os hábitos:", date.today())

    todas_conclusoes = deps["listar_conclusoes_uc"].listar(usuario)
    habitos_concluidos = [c for c in todas_conclusoes if c.data_registro.date() == data_escolhida]

    todos_habitos = deps["listar_habitos_uc"].executar(usuario)

    st.success(f"Hábitos em {data_escolhida.strftime('%d/%m/%Y')}:")
    if not todos_habitos:
        st.info("Nenhum hábito encontrado para esta data.")
    else:
        for h in todos_habitos:
            status = "⏳ Pendente"
            encontrado = next((c for c in habitos_concluidos if c.acao == h.acao and str(c.horario) == str(h.horario)), None)
            if encontrado:
                status = "✅ Concluído" if encontrado.status == "sim" else "❌ Não realizado"

            if f"editar_{h.id}" in st.session_state and st.session_state[f"editar_{h.id}"]:
                with st.form(f"form_editar_{h.id}"):
                    nova_acao = st.text_input("Ação:", value=h.acao, key=f"acao_{h.id}")
                    novo_horario = st.text_input("Horário (ex: 14h00):", value=str(h.horario), key=f"horario_{h.id}")
                    nova_categoria = st.text_input("Categoria:", value=h.categoria, key=f"categoria_{h.id}")
                    colf1, colf2 = st.columns([1, 1])
                    with colf1:
                        if st.form_submit_button("💾 Salvar"):
                            deps["atualizar_habito_uc"].executar(h.id, usuario,nova_acao, novo_horario, nova_categoria)
                            st.session_state[f"editar_{h.id}"] = False
                            st.rerun()
                    with colf2:
                        if st.form_submit_button("❌ Cancelar"):
                            st.session_state[f"editar_{h.id}"] = False
                            st.rerun()
            else:
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                with col1:
                    st.markdown(f"• **{h.acao}** às {str(h.horario)} — {status} ({h.categoria})")
                with col2:
                    if st.button("📝", key=f"btn_editar_{h.id}", help="Editar"):
                        st.session_state[f"editar_{h.id}"] = True
                        st.rerun()
                with col3:
                    if st.button("🗑️", key=f"remover_{h.id}", help="Remover"):
                        deps["apagar_habito_uc"].executar(h.id)
                        st.rerun()
                with col4:
                    if st.button("✅", key=f"concluir_{h.id}", help="Marcar como concluído"):
                        if has_uc("marcar_concluido_uc"):
                            deps["marcar_concluido_uc"].execute(habito_id=h.id, fonte_acao="calendario")
                        else:
                            deps["registrar_conclusao_uc"].executar(usuario, h.acao, str(h.horario), "sim", h.categoria)
                        st.rerun()
                with col5:
                    if st.button("❌", key=f"nao_{h.id}", help="Marcar como não realizado"):
                        deps["registrar_conclusao_uc"].executar(usuario, h.acao, str(h.horario), "não", h.categoria)
                        st.rerun()

    st.markdown("---")
    st.markdown("### 🎯 Filtros")
    categorias_disponiveis = ["", "alimentação", "hidratação", "exercício", "sono"]
    col1, col2 = st.columns(2)
    with col1:
        categoria_filtro = st.selectbox("Categoria:", categorias_disponiveis)
    with col2:
        data_range = st.date_input("Período:", [])

    btn_filtrar = st.button("🔍 Aplicar Filtros")

    if btn_filtrar:
        categoria = categoria_filtro if categoria_filtro else None
        data_inicio = data_range[0] if len(data_range) == 2 else None
        data_fim = data_range[1] if len(data_range) == 2 else None

        resultados = deps["listar_conclusoes_uc"].listar_filtrado(
            usuario=usuario,
            categoria=categoria,
            data_inicio=data_inicio.strftime("%Y-%m-%d") if data_inicio else None,
            data_fim=data_fim.strftime("%Y-%m-%d") if data_fim else None
        )
    else:
        resultados = deps["listar_conclusoes_uc"].listar(usuario)

    if resultados:
        total = len(resultados)
        concluidos = len([r for r in resultados if r.status == "sim"])
        nao_concluidos = total - concluidos
        taxa = (concluidos / total) * 100 if total > 0 else 0

        colA, colB, colC = st.columns(3)
        colA.metric("✅ Concluídos", concluidos)
        colB.metric("❌ Não realizados", nao_concluidos)
        colC.metric("📊 Taxa de Conclusão", f"{taxa:.1f}%")

        if taxa >= 80:
            st.success("🏅 Excelente desempenho! Você está cuidando muito bem dos seus hábitos!")
        elif taxa >= 50:
            st.info("💡 Bom trabalho! Continue nesse ritmo e tente melhorar um pouco mais!")
        else:
            st.warning("⚠️ Atenção! Que tal focar mais nos seus hábitos nos próximos dias?")

        st.markdown("---")
        st.markdown("### 🥧 Taxa de Conclusão")
        status_count = Counter([r.status for r in resultados])
        labels = list(status_count.keys())
        values = list(status_count.values())

        fig1, ax1 = plt.subplots()
        ax1.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
        ax1.axis("equal")
        st.pyplot(fig1)

        st.markdown("---")
        st.markdown("### 📈 Progresso ao Longo do Tempo")
        datas = [r.data_registro.date() for r in resultados]
        progresso_por_data = Counter(datas)
        datas_ordenadas = sorted(progresso_por_data.items())
        datas_labels = [d.strftime("%d/%m") for d, _ in datas_ordenadas]
        valores = [v for _, v in datas_ordenadas]

        fig_linha, ax_linha = plt.subplots()
        ax_linha.plot(datas_labels, valores, marker="o", linestyle="-", color="#4CAF50")
        ax_linha.set_title("Nº de Registros por Dia")
        ax_linha.set_xlabel("Data")
        ax_linha.set_ylabel("Total de hábitos registrados")
        st.pyplot(fig_linha)

        st.markdown("---")
        st.markdown("### 🕒 Distribuição por Horário")
        horarios = [str(r.horario) for r in resultados]
        horario_count = Counter(horarios)
        horario_sorted = dict(sorted(horario_count.items()))

        fig2, ax2 = plt.subplots()
        ax2.bar(horario_sorted.keys(), horario_sorted.values(), color="#2196F3")
        ax2.set_xlabel("Horário")
        ax2.set_ylabel("Quantidade")
        ax2.set_title("Frequência de Hábitos por Horário")
        st.pyplot(fig2)

        categorias = [r.categoria for r in resultados if r.categoria]
        if categorias:
            st.markdown("---")
            st.markdown("### 📂 Frequência por Categoria")
            cat_count = Counter(categorias)
            fig3, ax3 = plt.subplots()
            ax3.bar(cat_count.keys(), cat_count.values(), color="#FFC107")
            ax3.set_xlabel("Categoria")
            ax3.set_ylabel("Quantidade")
            ax3.set_title("Distribuição por Categoria")
            st.pyplot(fig3)
    else:
        st.warning("Nenhum dado disponível com os filtros aplicados.")