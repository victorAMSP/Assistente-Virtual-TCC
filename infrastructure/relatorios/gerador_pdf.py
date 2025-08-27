from fpdf import FPDF
from infrastructure.relatorios.relatorio_habitos import gerar_linhas_relatorio
from typing import List
from domain.entities.conclusao import Conclusao
import os
from datetime import date

def gerar_pdf(usuario: str, conclusoes: List[Conclusao]):
    linhas = gerar_linhas_relatorio(conclusoes)

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Relatório de Hábitos", ln=True, align="C")
    pdf.ln(10)

    for linha in linhas:
        pdf.set_x(pdf.l_margin) 
        pdf.multi_cell(pdf.epw, 10, txt=linha, new_x="LMARGIN", new_y="NEXT")

    nome_arquivo = f"relatorio_{usuario}.pdf"
    pdf.output(nome_arquivo)
