import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
from domain.entities.habito import Habito
from datetime import datetime, timedelta
from domain.entities.conclusao import Conclusao
from application.use_cases.registrar_habito_usecase import RegistrarHabitoUseCase
from application.use_cases.buscar_habitos_proximos_usecase import BuscarHabitosProximosUseCase
from application.use_cases.registrar_conclusao import RegistrarConclusaoUseCase
from application.use_cases.listar_habitos_usecase import ListarHabitosComIdUseCase
from application.use_cases.listar_conclusoes_usecase import ListarConclusoesUseCase
from application.use_cases.apagar_habito_por_id import ApagarHabitoPorIdUseCase
from application.use_cases.atualizar_habito_usecase import AtualizarHabitoUseCase
from domain.repositories.conclusao_repository import ConclusaoRepository
from application.use_cases.gerar_relatorio_pdf_usecase import GerarRelatorioPDFUseCase

class TestRegistrarHabitoUseCase(unittest.TestCase):
    def test_registrar_habito(self):
        # Arrange
        mock_repo = MagicMock()
        use_case = RegistrarHabitoUseCase(mock_repo)

        # Act
        use_case.executar(
            usuario="victor",
            acao="beber água",
            horario="08:00",
            categoria="hidratação"
        )

        # Assert
        mock_repo.salvar.assert_called_once()
        habito_salvo = mock_repo.salvar.call_args[0][0]
        self.assertIsInstance(habito_salvo, Habito)
        self.assertEqual(habito_salvo.usuario, "victor")
        self.assertEqual(habito_salvo.acao, "beber água")
        self.assertEqual(habito_salvo.horario, "08:00")
        self.assertEqual(habito_salvo.categoria, "hidratação")

class TestBuscarHabitosProximosUseCase(unittest.TestCase):
    def test_buscar_habitos_proximos(self):
        # Arrange
        repo_mock = MagicMock()
        use_case = BuscarHabitosProximosUseCase(repo_mock)

        usuario = "victor"
        tolerancia = 30  # minutos

        # Simulamos que o repositório já retorna só os hábitos dentro da faixa
        repo_mock.buscar_proximos.return_value = [
            Habito(usuario, "hábito 1", "13:45", "categoria"),
            Habito(usuario, "hábito 2", "14:15", "categoria"),
        ]

        # Act
        encontrados = use_case.executar(usuario, tolerancia)

        # Assert
        self.assertEqual(len(encontrados), 2)
        acoes = [h.acao for h in encontrados]
        self.assertIn("hábito 1", acoes)
        self.assertIn("hábito 2", acoes)

class TestRegistrarConclusaoUseCase(unittest.TestCase):
    def test_registrar_conclusao(self):
        # Arrange
        repo_mock = MagicMock()
        use_case = RegistrarConclusaoUseCase(repo_mock)

        # Dados de entrada
        usuario = "victor"
        acao = "ler"
        horario = "22:00"
        status = "sim"
        categoria = "lazer"

        # Act
        use_case.executar(usuario, acao, horario, status, categoria)

        # Assert
        repo_mock.registrar.assert_called_once()
        conclusao = repo_mock.registrar.call_args[0][0]

        self.assertIsInstance(conclusao, Conclusao)
        self.assertEqual(conclusao.usuario, usuario)
        self.assertEqual(conclusao.acao, acao)
        self.assertEqual(conclusao.horario, horario)
        self.assertEqual(conclusao.status, status)
        self.assertEqual(conclusao.categoria, categoria)
        self.assertIsNotNone(conclusao.data_registro)

class TestListarHabitosComIdUseCase(unittest.TestCase):
    def test_listar_habitos_com_id(self):
        # Arrange
        repo_mock = MagicMock()
        use_case = ListarHabitosComIdUseCase(repo_mock)

        usuario = "victor"
        habitos_mock = [
            Habito(usuario, "beber água", "08:00", "hidratação", id=1),
            Habito(usuario, "caminhar", "18:00", "exercício", id=2)
        ]
        repo_mock.listar_com_id.return_value = habitos_mock

        # Act
        resultado = use_case.executar(usuario)

        # Assert
        repo_mock.listar_com_id.assert_called_once_with(usuario)
        self.assertEqual(resultado, habitos_mock)
        self.assertEqual(resultado[0].id, 1)
        self.assertEqual(resultado[1].acao, "caminhar")

class TestListarConclusoesUseCase(unittest.TestCase):
    def test_listar_conclusoes(self):
        repo_mock = MagicMock()
        use_case = ListarConclusoesUseCase(repo_mock)

        usuario = "victor"
        conclusoes_mock = [
            Conclusao(usuario, "beber água", "08:00", "sim", datetime.now(), "hidratação"),
            Conclusao(usuario, "correr", "07:00", "sim", datetime.now(), "exercício")
        ]
        repo_mock.listar.return_value = conclusoes_mock

        resultado = use_case.listar(usuario)

        repo_mock.listar.assert_called_once_with(usuario)
        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[0].acao, "beber água")
        self.assertEqual(resultado[1].categoria, "exercício")

    def test_listar_conclusoes_filtrado(self):
        repo_mock = MagicMock()
        use_case = ListarConclusoesUseCase(repo_mock)

        usuario = "victor"
        categoria = "exercício"
        data_inicio = datetime(2024, 1, 1).date()
        data_fim = datetime(2025, 12, 31).date()

        conclusoes_mock = [
            Conclusao(usuario, "correr", "07:00", "sim", datetime(2025, 6, 1, 7, 0), "exercício"),
            Conclusao(usuario, "fazer musculação", "18:00", "sim", datetime(2025, 5, 30, 18, 0), "exercício")
        ]
        repo_mock.listar_filtrado.return_value = conclusoes_mock

        resultado = use_case.listar_filtrado(usuario, categoria, data_inicio, data_fim)

        repo_mock.listar_filtrado.assert_called_once_with(
            usuario=usuario,
            categoria=categoria,
            data_inicio=data_inicio,
            data_fim=data_fim
        )
        self.assertEqual(len(resultado), 2)
        self.assertTrue(all(c.categoria == "exercício" for c in resultado))

class TestApagarHabitoPorIdUseCase(unittest.TestCase):
    def test_apagar_habito_por_id(self):
        repo_mock = MagicMock()
        use_case = ApagarHabitoPorIdUseCase(repo_mock)

        id_habito = 1

        use_case.executar(id_habito)

        repo_mock.apagar_por_id.assert_called_once_with(id_habito)

class TestAtualizarHabitoUseCase(unittest.TestCase):
    def test_atualizar_habito(self):
        repo_mock = MagicMock()
        use_case = AtualizarHabitoUseCase(repo_mock)

        id_habito = 1
        nova_acao = "beber água"
        novo_horario = "08:00"
        nova_categoria = "hidratação"

        use_case.executar(id_habito, nova_acao, novo_horario, nova_categoria)

        # O Habito gerado internamente no use case deve ser equivalente ao seguinte:
        esperado = Habito(usuario="", acao=nova_acao, horario=novo_horario, categoria=nova_categoria, id=id_habito)

        # Verifica se o método atualizar foi chamado com um objeto equivalente
        repo_mock.atualizar.assert_called_once()
        chamado = repo_mock.atualizar.call_args[0][0]  # Pega o primeiro argumento da chamada

        self.assertEqual(chamado.id, esperado.id)
        self.assertEqual(chamado.acao, esperado.acao)
        self.assertEqual(chamado.horario, esperado.horario)
        self.assertEqual(chamado.categoria, esperado.categoria)
        self.assertEqual(chamado.usuario, esperado.usuario)

class TestRegistrarConclusaoUseCase(unittest.TestCase):
    def test_registrar_conclusao(self):
        repo_mock = MagicMock()
        use_case = RegistrarConclusaoUseCase(repo_mock)

        usuario = "victor"
        acao = "correr"
        horario = "07:00"
        status = "sim"
        categoria = "exercício"

        use_case.executar(usuario, acao, horario, status, categoria)

        repo_mock.registrar.assert_called_once()
        chamada = repo_mock.registrar.call_args[0][0]

        self.assertEqual(chamada.usuario, usuario)
        self.assertEqual(chamada.acao, acao)
        self.assertEqual(chamada.horario, horario)
        self.assertEqual(chamada.status, status)
        self.assertEqual(chamada.categoria, categoria)

class TestGerarRelatorioPDFUseCase(TestCase):
    def test_gerar_relatorio_pdf(self):
        repo_mock = MagicMock()
        gerar_pdf_mock = MagicMock()
        usuario = "victor"
        conclusoes_mock = [
            Conclusao(usuario="victor", acao="correr", horario="07:00", status="sim", categoria="exercício")
        ]
        repo_mock.listar.return_value = conclusoes_mock

        use_case = GerarRelatorioPDFUseCase(conclusao_repo=repo_mock, gerar_pdf_func=gerar_pdf_mock)
        use_case.executar(usuario)

        repo_mock.listar.assert_called_once_with(usuario)
        gerar_pdf_mock.assert_called_once_with(usuario, conclusoes_mock)

if __name__ == '__main__':
    unittest.main()
