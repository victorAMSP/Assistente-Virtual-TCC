from domain.value_objects.horario_do_habito import HorarioDoHabito

class Habito:
    def __init__(
            self, 
            usuario: str, 
            acao: str, 
            horario: HorarioDoHabito, 
            categoria: str = "geral", 
            id: int = None):
        
        if not usuario or not usuario.strip():
            raise ValueError("Usuário do hábito não pode ser vazio")

        if not acao or not acao.strip():
            raise ValueError("Ação do hábito não pode ser vazia")

        if not isinstance(horario, HorarioDoHabito):
            raise TypeError("Horário deve ser um HorarioDoHabito")
        
        categoria_normalizada = categoria.strip().lower() if categoria and categoria.strip() else "geral"

        self.id = id                                # Identificador único no banco
        self.usuario = usuario.strip()              # Usuário ao qual o hábito pertence
        self.acao = acao.strip().lower()            # Ex: 'beber água'
        self.horario = horario                      # Ex: '14h00'
        self.categoria = categoria_normalizada      # Ex: 'hidratação'

    def __str__(self):
        return f"{self.acao} às {self.horario} ({self.categoria})"