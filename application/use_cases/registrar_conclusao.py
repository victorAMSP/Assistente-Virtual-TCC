from domain.entities.conclusao import Conclusao
from domain.repositories.conclusao_repository import ConclusaoRepository
from datetime import datetime
from domain.value_objects.horario_do_habito import HorarioDoHabito

class RegistrarConclusaoUseCase:
    def __init__(self, conclusao_repository: ConclusaoRepository):
        self.conclusao_repository = conclusao_repository

    def executar(self, usuario: str, acao: str, horario: str, status: str, categoria: str):

        horario_vo = HorarioDoHabito.from_string(horario)

        conclusao = Conclusao(
            usuario=usuario,
            acao=acao,
            horario=horario_vo,
            status=status,
            data_registro=datetime.now(),
            categoria=categoria
        )
        self.conclusao_repository.registrar(conclusao)