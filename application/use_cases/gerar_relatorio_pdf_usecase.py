from domain.repositories.conclusao_repository import ConclusaoRepository
from typing import Callable, List
from domain.entities.conclusao import Conclusao
from infrastructure.relatorios.gerador_pdf import gerar_pdf

class GerarRelatorioPDFUseCase:
    def __init__(
        self,
        conclusao_repo: ConclusaoRepository,
        gerar_pdf_func: Callable[[str, List[Conclusao]], None] = gerar_pdf
    ):
        self.conclusao_repo = conclusao_repo
        self.gerar_pdf = gerar_pdf_func  

    def executar(self, usuario: str):
        conclusoes = self.conclusao_repo.listar(usuario)
        self.gerar_pdf(usuario, conclusoes) 