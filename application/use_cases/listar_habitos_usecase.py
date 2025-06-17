from domain.repositories.habito_repository import IHabitorepository

class ListarHabitosComIdUseCase:
    def __init__(self, habito_repository: IHabitorepository):
        self.habito_repository = habito_repository

    def executar(self, usuario: str):
        return self.habito_repository.listar_com_id(usuario)
    
