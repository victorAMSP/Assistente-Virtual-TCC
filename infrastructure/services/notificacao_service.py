# from application.use_cases.buscar_habitos_proximos_usecase import BuscarHabitosProximosUseCase
# from plyer import notification

# class NotificacaoService:
#     def __init__(self, buscar_habitos_uc: BuscarHabitosProximosUseCase):
#         self.buscar_habitos_uc = buscar_habitos_uc
#         self.notificados = set()

#     def verificar_e_notificar(self, usuario: str):
#         habitos = self.buscar_habitos_uc.executar(usuario)

#         for h in habitos:
#             horario_str = str(h.horario)
#             chave = f"{h.acao}_{horario_str}"
#             if chave in self.notificados:
#                 continue

#             titulo = f"Lembrete: {h.acao}"
#             mensagem = f"Está na hora de '{h.acao}' às {horario_str} ({h.categoria})"
#             self._notificar(titulo, mensagem)
#             self.notificados.add(chave)

#     def _notificar(self, titulo: str, mensagem: str):
#         notification.notify(
#             title=titulo,
#             message=mensagem,
#             app_name="Assistente Virtual",
#             timeout=10
#         )
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from application.use_cases.buscar_habitos_proximos_usecase import BuscarHabitosProximosUseCase
from plyer import notification


class NotificacaoService:
    """Dispara e gerencia lembretes (estado TEMPORÁRIO em memória).

    - Não altera o Hábito no banco.
    - Mantém estado da sessão atual:
        * notificados: já notificados recentemente (evita spam a cada rerun)
        * snoozed_until: adiados (só notificar após esse horário)
        * consumidos: já respondidos (concluído/não concluído) e não devem reaparecer
    """

    def __init__(self, buscar_habitos_uc: BuscarHabitosProximosUseCase):
        self.buscar_habitos_uc = buscar_habitos_uc
        self.notificados: set[str] = set()
        self.snoozed_until: dict[str, datetime] = {}
        self.consumidos: set[str] = set()

    def gerar_chave(self, acao: str, horario_str: str) -> str:
        return f"{acao}_{horario_str}"

    def adiar(self, chave: str, minutos: int = 15) -> None:
        """Adia um lembrete e libera para re-notificar após o snooze."""
        dt = datetime.now() + timedelta(minutes=minutos)
        self.snoozed_until[chave] = dt
        self.notificados.discard(chave)  # permite nova notificação depois do snooze

    def consumir(self, chave: str) -> None:
        """Marca o lembrete como respondido (não reaparece)."""
        self.consumidos.add(chave)
        self.notificados.discard(chave)
        self.snoozed_until.pop(chave, None)

    def get_snooze_until(self, chave: str) -> Optional[datetime]:
        return self.snoozed_until.get(chave)

    def pode_notificar(self, chave: str, agora: Optional[datetime] = None) -> bool:
        if chave in self.consumidos:
            return False
        if chave in self.notificados:
            return False

        agora = agora or datetime.now()
        until = self.snoozed_until.get(chave)
        if until is not None and agora < until:
            return False

        # Snooze expirou: libera e limpa
        if until is not None and agora >= until:
            self.snoozed_until.pop(chave, None)

        return True

    def verificar_e_notificar(self, usuario: str):
        habitos = self.buscar_habitos_uc.executar(usuario)
        agora = datetime.now()

        for h in habitos:
            horario_str = str(h.horario)
            chave = self.gerar_chave(h.acao, horario_str)

            if not self.pode_notificar(chave, agora=agora):
                continue

            titulo = f"Lembrete: {h.acao}"
            mensagem = f"Está na hora de '{h.acao}' às {horario_str} ({h.categoria})"
            self._notificar(titulo, mensagem)

            # Anti-spam em reruns. Se o usuário der snooze, adiar() remove.
            self.notificados.add(chave)

    def _notificar(self, titulo: str, mensagem: str):
        notification.notify(
            title=titulo,
            message=mensagem,
            app_name="Assistente Virtual",
            timeout=10,
        )