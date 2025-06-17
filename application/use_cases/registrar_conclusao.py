from domain.entities.conclusao import Conclusao
from domain.repositories.conclusao_repository import ConclusaoRepository
from datetime import datetime

class RegistrarConclusaoUseCase:
    def __init__(self, conclusao_repository: ConclusaoRepository):
        self.conclusao_repository = conclusao_repository

    def executar(self, usuario: str, acao: str, horario: str, status: str, categoria: str):
        conclusao = Conclusao(
            usuario=usuario,
            acao=acao,
            horario=horario,
            status=status,
            data_registro=datetime.now(),
            categoria=categoria
        )
        self.conclusao_repository.registrar(conclusao)