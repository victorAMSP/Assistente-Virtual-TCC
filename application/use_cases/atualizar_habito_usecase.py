from domain.repositories.habito_repository import IHabitorepository
from domain.entities.habito import Habito
from domain.value_objects.horario_do_habito import HorarioDoHabito  

class AtualizarHabitoUseCase:
    def __init__(self, habito_repo: IHabitorepository):
        self.habito_repo = habito_repo

    def executar(self, id: int, usuario: str, acao: str, horario: str, categoria: str):
        # converte a string recebida em VO
        horario_vo = HorarioDoHabito.from_string(horario)

        habito = Habito(
            id=id,
            usuario=usuario,
            acao=acao,
            horario=horario_vo,  
            categoria=categoria,
        )

        self.habito_repo.atualizar(habito)