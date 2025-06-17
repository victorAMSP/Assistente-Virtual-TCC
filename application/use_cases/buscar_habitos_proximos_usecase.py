from domain.repositories.habito_repository import IHabitorepository

class BuscarHabitosProximosUseCase:
    def __init__(self, habito_repo: IHabitorepository):
        self.habito_repo = habito_repo

    def executar(self, usuario: str, tolerancia_min: int = 5):
        return self.habito_repo.buscar_proximos(usuario, tolerancia_min)