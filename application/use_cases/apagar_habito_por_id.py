from domain.repositories.habito_repository import IHabitorepository

class ApagarHabitoPorIdUseCase:
    def __init__(self, habito_repository: IHabitorepository):
        self.habito_repository = habito_repository

    def executar(self, habito_id: int):
        self.habito_repository.apagar_por_id(habito_id)