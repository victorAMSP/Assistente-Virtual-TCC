from domain.repositories.conclusao_repository import ConclusaoRepository
from typing import Optional, List
from datetime import date

class ListarConclusoesUseCase:
    def __init__(self, conclusao_repository: ConclusaoRepository):
        self.conclusao_repository = conclusao_repository

    def listar(self, usuario: str) -> List[tuple]:
        return self.conclusao_repository.listar(usuario)

    def listar_filtrado(
        self,
        usuario: str,
        categoria: Optional[str] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> List[tuple]:
        return self.conclusao_repository.listar_filtrado(
            usuario=usuario,
            categoria=categoria,
            data_inicio=data_inicio,
            data_fim=data_fim
        )