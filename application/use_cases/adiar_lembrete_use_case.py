from infrastructure.services.notificacao_service import NotificacaoService

class AdiarLembreteUseCase:
    def __init__(self, notificador: NotificacaoService):
        self.notificador = notificador

    def execute(self, chave: str, minutos: int = 15) -> bool:
        if not chave or not isinstance(chave, str):
            return False
        if not isinstance(minutos, int) or minutos <= 0:
            return False

        self.notificador.adiar(chave, minutos=minutos)
        return True