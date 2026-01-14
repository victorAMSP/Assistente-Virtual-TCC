from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class CategoriaDoHabito:
    valor: str

    def __post_init__(self):
        normalizada = self._normalizar(self.valor)
        if not normalizada:
            raise ValueError("Categoria do hábito não pode ser vazia.")
        if len(normalizada) > 30:
            raise ValueError("Categoria do hábito muito longa (máx. 30 caracteres).")
        object.__setattr__(self, "valor", normalizada)

    @staticmethod
    def _normalizar(texto: str) -> str:
        if texto is None:
            return ""
        # trim + lower + remove espaços duplicados
        return " ".join(str(texto).strip().lower().split())

    @classmethod
    def from_string(cls, texto: str) -> "CategoriaDoHabito":
        return cls(texto)

    def to_db(self) -> str:
        return self.valor

    @classmethod
    def from_db(cls, texto: str) -> "CategoriaDoHabito":
        return cls(texto)

    def __str__(self) -> str:
        return self.valor