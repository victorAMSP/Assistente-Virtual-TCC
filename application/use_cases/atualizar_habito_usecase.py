from domain.repositories.habito_repository import IHabitorepository
from domain.entities.habito import Habito
from domain.value_objects.horario_do_habito import HorarioDoHabito
from domain.value_objects.categoria_do_habito import CategoriaDoHabito  

class AtualizarHabitoUseCase:
    def __init__(self, habito_repo: IHabitorepository):
        self.habito_repo = habito_repo

    def executar(self, id: int, usuario: str, acao: str, horario: str, categoria: str):
        # converte a string recebida em VO
        horario_vo = HorarioDoHabito.from_string(horario)
        categoria_vo = CategoriaDoHabito.from_string(categoria)

        habito = Habito(
            id=id,
            usuario=usuario,
            acao=acao,
            horario=horario_vo,  
            categoria=categoria_vo,
        )

        self.habito_repo.atualizar(habito)