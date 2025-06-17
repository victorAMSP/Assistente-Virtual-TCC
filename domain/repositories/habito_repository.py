from abc import ABC, abstractmethod
from typing import List
from domain.entities.habito import Habito

class IHabitorepository(ABC):
    @abstractmethod
    def salvar(self, habito: Habito) -> None:
        pass

    @abstractmethod
    def listar_por_usuario(self, usuario: str) -> List[Habito]:
        pass

    @abstractmethod
    def listar_com_id(self, usuario: str) -> List[Habito]:
        pass

    @abstractmethod
    def apagar_por_id(self, id: int) -> None:
        pass

    @abstractmethod
    def atualizar(self, habito: Habito) -> None:
        pass

    @abstractmethod
    def buscar_proximos(self, usuario: str, tolerancia_min: int) -> List[Habito]:
        pass
    