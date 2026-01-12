from domain.entities.habito import Habito
from domain.repositories.habito_repository import IHabitorepository
from domain.value_objects.horario_do_habito import HorarioDoHabito

class RegistrarHabitoUseCase:
    def __init__(self, habito_repo: IHabitorepository):
        self.habito_repo = habito_repo

    def executar(self, usuario: str, acao: str, horario: str, categoria: str = "geral"):
        # 1) Converte string -> Value Object (valida horário)
        horario_vo = HorarioDoHabito.from_string(horario)

        # 2) Verifica se já existe o mesmo hábito (usuario + acao + horario)
        habitos_existentes = self.habito_repo.listar_por_usuario(usuario)

        for h in habitos_existentes:
            mesmo_horario = (h.horario == horario_vo)

            if h.acao == acao and mesmo_horario:
                # Já existe: retorna o hábito existente (não cria duplicado)
                return h

        # 3) Se não existe, cria e salva
        novo_habito = Habito(usuario=usuario, acao=acao, horario=horario_vo, categoria=categoria)
        self.habito_repo.salvar(novo_habito)
        return novo_habito