from domain.repositories.habito_repository import IHabitorepository
from domain.entities.habito import Habito

class AtualizarHabitoUseCase:
    def __init__(self, habito_repo: IHabitorepository):
        self.habito_repo = habito_repo

    def executar(self, id_habito: int, nova_acao: str, novo_horario: str, nova_categoria: str):
        novo_habito = Habito(usuario="", acao=nova_acao, horario=novo_horario, categoria=nova_categoria, id=id_habito)
        self.habito_repo.atualizar(novo_habito) 