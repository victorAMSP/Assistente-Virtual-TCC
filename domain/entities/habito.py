class Habito:
    def __init__(self, usuario: str, acao: str, horario: str, categoria: str, id: int = None):
        self.id = id                  # Identificador único no banco
        self.usuario = usuario        # Usuário ao qual o hábito pertence
        self.acao = acao              # Ex: 'beber água'
        self.horario = horario        # Ex: '14h00'
        self.categoria = categoria    # Ex: 'hidratação'

    def __str__(self):
        return f"{self.acao} às {self.horario} ({self.categoria})"