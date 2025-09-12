from application.use_cases.buscar_habitos_proximos_usecase import BuscarHabitosProximosUseCase
from plyer import notification

class NotificacaoService:
    def __init__(self, buscar_habitos_uc: BuscarHabitosProximosUseCase):
        self.buscar_habitos_uc = buscar_habitos_uc
        self.notificados = set()

    def verificar_e_notificar(self, usuario: str):
        habitos = self.buscar_habitos_uc.executar(usuario)

        for h in habitos:
            horario_str = str(h.horario)
            chave = f"{h.acao}_{horario_str}"
            if chave in self.notificados:
                continue

            titulo = f"Lembrete: {h.acao}"
            mensagem = f"Está na hora de '{h.acao}' às {horario_str} ({h.categoria})"
            self._notificar(titulo, mensagem)
            self.notificados.add(chave)

    def _notificar(self, titulo: str, mensagem: str):
        notification.notify(
            title=titulo,
            message=mensagem,
            app_name="Assistente Virtual",
            timeout=10
        )