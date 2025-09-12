from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.conclusao import Conclusao

class ConclusaoRepository(ABC):
    # @abstractmethod
    # def salvar(self, conclusao: Conclusao) -> None:
    #     """Salva uma nova conclusão no banco de dados."""
    #     pass

    @abstractmethod
    def registrar(self, conclusao: Conclusao) -> None:
        pass

    @abstractmethod
    def listar(self, usuario: str) -> List[Conclusao]:
        pass

    @abstractmethod
    def listar_por_usuario(self, usuario: str) -> List[Conclusao]:
        """Retorna todas as conclusões de um usuário."""
        pass

    @abstractmethod
    def listar_filtrado(self, usuario: str, categoria: Optional[str], data_inicio: Optional[str], data_fim: Optional[str]) -> List[Conclusao]:
        """Lista conclusões filtrando por categoria e intervalo de datas."""
        pass