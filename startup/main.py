from infrastructure.repositories.habito_repository_sqlite import HabitoRepositorySQLite
from infrastructure.repositories.conclusao_repository_sqlite import ConclusaoRepositorySQLite
from application.use_cases import (
    RegistrarHabitoUseCase,
    ListarHabitosComIdUseCase,
    ApagarHabitoPorIdUseCase,
    AtualizarHabitoUseCase,
    RegistrarConclusaoUseCase,
    ListarConclusoesUseCase,
    BuscarHabitosProximosUseCase,
    GerarRelatorioPDFUseCase,
)
from application.use_cases.adiar_habito_use_case import AdiarHabitoUseCase
from application.use_cases.marcar_concluido_use_case import MarcarConcluidoUseCase
from domain.services.processador_comando_service import ProcessadorComandoService
from infrastructure.services.notificacao_service import NotificacaoService

def configurar_dependencias():
    # Repositórios
    habito_repo = HabitoRepositorySQLite()
    conclusao_repo = ConclusaoRepositorySQLite()

    registrar_habito_uc = RegistrarHabitoUseCase(habito_repo)
    listar_habitos_uc = ListarHabitosComIdUseCase(habito_repo)
    apagar_habito_uc = ApagarHabitoPorIdUseCase(habito_repo)
    atualizar_habito_uc = AtualizarHabitoUseCase(habito_repo)
    registrar_conclusao_uc = RegistrarConclusaoUseCase(conclusao_repo)
    listar_conclusoes_uc = ListarConclusoesUseCase(conclusao_repo)
    buscar_proximos_uc = BuscarHabitosProximosUseCase(habito_repo)
    gerar_relatorio_uc = GerarRelatorioPDFUseCase(conclusao_repo)
    adiar_habito_uc = AdiarHabitoUseCase(habito_repo)
    marcar_concluido_uc = MarcarConcluidoUseCase(habito_repo, registrar_conclusao_uc)

    processador = ProcessadorComandoService()
    notificador = NotificacaoService(buscar_proximos_uc)

    return {
        "registrar_habito_uc": registrar_habito_uc,
        "listar_habitos_uc": listar_habitos_uc,
        "apagar_habito_uc": apagar_habito_uc,
        "atualizar_habito_uc": atualizar_habito_uc,
        "registrar_conclusao_uc": registrar_conclusao_uc,
        "listar_conclusoes_uc": listar_conclusoes_uc,
        "buscar_proximos_uc": buscar_proximos_uc,
        "gerar_relatorio_uc": gerar_relatorio_uc,
        "processador": processador,
        "notificador": notificador,
        "adiar_habito_uc": adiar_habito_uc,
        "marcar_concluido_uc": marcar_concluido_uc,
    }
