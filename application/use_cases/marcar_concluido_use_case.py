from __future__ import annotations

from application.use_cases.registrar_conclusao import RegistrarConclusaoUseCase
from domain.repositories.habito_repository import IHabitorepository

class MarcarConcluidoUseCase:

    def __init__(
        self,
        habito_repo: IHabitorepository,
        registrar_conclusao_uc: RegistrarConclusaoUseCase,
    ):
        self.habito_repo = habito_repo
        self.registrar_conclusao_uc = registrar_conclusao_uc

    def execute(self, habito_id: int, fonte_acao: str = "chatbot") -> bool:
        # Validação básica
        if not isinstance(habito_id, int):
            return False

        # 1) Busca o hábito 
        habito = self.habito_repo.buscar_por_id(habito_id)
        if habito is None:
            return False

        # 2) Registra no histórico de conclusões
        self.registrar_conclusao_uc.executar(
            usuario=habito.usuario,
            acao=habito.acao,
            horario=str(habito.horario),
            status="sim",
            categoria=str(habito.categoria),
        )

        return True