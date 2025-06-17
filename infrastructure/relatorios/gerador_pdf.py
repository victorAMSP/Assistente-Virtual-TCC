from fpdf import FPDF
from infrastructure.relatorios.relatorio_habitos import gerar_linhas_relatorio
from typing import List
from domain.entities.conclusao import Conclusao

def gerar_pdf(usuario: str, conclusoes: List[Conclusao]):
    linhas = gerar_linhas_relatorio(conclusoes)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Relatório de Hábitos", ln=True, align="C")
    pdf.ln(10)

    for linha in linhas:
        pdf.multi_cell(0, 10, txt=linha)

    nome_arquivo = f"relatorio_{usuario}.pdf"
    pdf.output(nome_arquivo)