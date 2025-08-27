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
# class GerarRelatorioPDFUseCase:
#     """
#     Construtor retrocompatível:
#     - Antigo: GerarRelatorioPDFUseCase(conclusao_repo)
#     - Novo:   GerarRelatorioPDFUseCase(listar_conclusoes_uc, gerar_pdf)
#     """

#     def __init__(self, dep1, gerar_pdf=None):
#         # 1) Resolver a função geradora de PDF
#         if gerar_pdf is None:
#             try:
#                 from infrastructure.relatorios.gerador_pdf import gerar_pdf as _gerar_pdf
#             except Exception as e:
#                 raise RuntimeError(
#                     "Não foi possível importar a função gerar_pdf padrão."
#                 ) from e
#             self.gerar_pdf = _gerar_pdf
#         else:
#             self.gerar_pdf = gerar_pdf

#         # 2) Resolver o 'listar_conclusoes_uc'
#         # Se 'dep1' já for um UC (tem algum método público típico), usa direto;
#         # caso contrário, embrulha o repositório num UC de listar.
#         if hasattr(dep1, "executar") or hasattr(dep1, "listar"):
#             self.listar_conclusoes_uc = dep1
#         else:
#             try:
#                 from application.use_cases.listar_conclusoes_usecase import ListarConclusoesUseCase
#             except ImportError:
#                 # caso o nome do arquivo seja com "_use_case"
#                 from application.use_cases.listar_conclusoes_usecase import ListarConclusoesUseCase
#             self.listar_conclusoes_uc = ListarConclusoesUseCase(dep1)

#     def _listar_conclusoes(self, usuario, data_inicio=None, data_fim=None, categoria=None):
#         uc = self.listar_conclusoes_uc

#         # Preferência: executar(...)
#         if hasattr(uc, "executar"):
#             return uc.executar(
#                 usuario,
#                 data_inicio=data_inicio,
#                 data_fim=data_fim,
#                 categoria=categoria,
#             )

#         # Fallback: listar(...) com diferentes assinaturas
#         if hasattr(uc, "listar"):
#             try:
#                 # Assinatura completa
#                 return uc.listar(usuario, data_inicio=data_inicio, data_fim=data_fim, categoria=categoria)
#             except TypeError:
#                 # Assinaturas reduzidas (tenta algumas variações comuns)
#                 try:
#                     return uc.listar(usuario, data_inicio, data_fim)
#                 except TypeError:
#                     try:
#                         return uc.listar(usuario)
#                     except TypeError:
#                         pass

#         raise RuntimeError(
#             "ListarConclusoesUseCase não possui métodos esperados ('executar' ou 'listar')."
#         )

#     def executar(self, usuario, data_inicio=None, data_fim=None, categoria=None):
#         conclusoes = self._listar_conclusoes(
#             usuario,
#             data_inicio=data_inicio,
#             data_fim=data_fim,
#             categoria=categoria,
#         )
#         # Se o gerador retorna caminho, repasse; se não, retorna None (mantém compatibilidade)
#         return self.gerar_pdf(usuario, conclusoes)