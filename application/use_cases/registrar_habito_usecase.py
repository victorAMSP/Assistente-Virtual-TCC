from domain.entities.habito import Habito
from domain.repositories.habito_repository import IHabitorepository

class RegistrarHabitoUseCase:
    def __init__(self, habito_repo: IHabitorepository):
        self.habito_repo = habito_repo

    def executar(self, usuario: str, acao: str, horario: str, categoria: str):
        """
        Orquestra o processo de criação de um novo hábito no sistema.
        """
        # Cria uma instância da entidade
        novo_habito = Habito(usuario=usuario, acao=acao, horario=horario, categoria=categoria)

        # Chama o repositório para persistir
        self.habito_repo.salvar(novo_habito)

        # Retorna o hábito registrado (pode ser útil para logs ou testes)
        return novo_habito