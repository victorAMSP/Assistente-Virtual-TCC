from domain.entities.conclusao import Conclusao
from typing import List

def gerar_linhas_relatorio(conclusoes: List[Conclusao]) -> List[str]:
    linhas = []
    for c in conclusoes:
        status = "Concluído" if c.status == "sim" else "Não realizado"
        data = c.data_registro.strftime("%d/%m/%Y %H:%M")
        linhas.append(f"{data} - {c.acao} às {c.horario} ({c.categoria}) - {status}")
    return linhas