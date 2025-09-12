from datetime import datetime
from domain.value_objects.horario_do_habito import HorarioDoHabito


class Conclusao:
    def __init__(self, usuario, acao, horario: HorarioDoHabito, status, data_registro=None, categoria="geral", id=None):
        self.id = id                      # ID único da conclusão
        self.usuario = usuario            # Usuário dono da conclusão
        self.acao = acao                  # Ação concluída
        self.horario = horario            # Ex: '14h00'
        self.status = status              # 'sim' ou 'não'
        self.categoria = categoria        # Ex: 'exercício', 'sono'
        self.data_registro = data_registro or datetime.now()  # Data e hora da conclusão

    def __str__(self):
        return f"{self.acao} às {self.horario} - {self.status} ({self.categoria}) em {self.data_registro.strftime('%d/%m/%Y')}"