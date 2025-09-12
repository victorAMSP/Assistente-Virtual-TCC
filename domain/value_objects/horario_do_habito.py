
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import time

__all__ = ["HorarioDoHabito"]


@dataclass(frozen=True)
class HorarioDoHabito:
    """Value Object para o horário alvo de um hábito (sem data).

    - Imutável e com igualdade por valor
    - Aceita entradas: "07h30", "07:30", "0730", "7", "07:30:00", "07.30", "07 30"
    - Persistência e exibição: **"HHhMM"** (ex.: "07h30")
    """

    valor: time

    # ------------------------------
    # Construção
    # ------------------------------
    @classmethod
    def from_string(cls, texto: str) -> "HorarioDoHabito":
        if texto is None:
            raise ValueError("texto não pode ser None")
        s = str(texto).strip().lower()
        if not s:
            raise ValueError("horário vazio")

        # Normaliza separadores para ':' temporariamente
        s_norm = s.replace(" ", "").replace("h", ":").replace(".", ":")

        # Apenas dígitos: "7" -> 07:00, "730"/"0730" -> 07:30
        if re.fullmatch(r"\d{1,4}", s_norm):
            if len(s_norm) <= 2:
                h = int(s_norm); m = 0; sec = 0
            else:
                h = int(s_norm[:-2]); m = int(s_norm[-2:]); sec = 0
            _validate_hms(h, m, sec)
            return cls(time(hour=h, minute=m, second=sec))

        partes = s_norm.split(":")
        if not 1 <= len(partes) <= 3:
            raise ValueError(f"formato de horário inválido: '{texto}'")
        try:
            h = int(partes[0]) if partes[0] else 0
            m = int(partes[1]) if len(partes) >= 2 and partes[1] else 0
            sec = int(partes[2]) if len(partes) == 3 and partes[2] else 0
        except ValueError as e:
            raise ValueError(f"componentes de horário devem ser numéricos: '{texto}'") from e

        _validate_hms(h, m, sec)
        return cls(time(hour=h, minute=m, second=sec))

    @classmethod
    def from_time(cls, t: time) -> "HorarioDoHabito":
        if not isinstance(t, time):
            raise TypeError("t deve ser datetime.time")
        return cls(t.replace(microsecond=0))

    @classmethod
    def from_db(cls, texto: str) -> "HorarioDoHabito":
        """Aceita o que estiver no banco; padrão do projeto é "HHhMM" (ex.: "07h30")."""
        return cls.from_string(texto)

    # ------------------------------
    # Conversões / Exibição
    # ------------------------------
    def to_db(self) -> str:
        """Representação para persistência no formato "HHhMM" (ex.: "07h30")."""
        return self.valor.strftime("%Hh%M")

    def as_user(self) -> str:
        """Formato amigável ao usuário (igual ao do banco)."""
        return self.to_db()

    def as_hhmm(self) -> str:
        return self.valor.strftime("%H:%M")

    def as_hhmmss(self) -> str:
        return self.valor.strftime("%H:%M:%S")

    # ------------------------------
    # Acessores / Utilidades
    # ------------------------------
    @property
    def hora(self) -> int:
        return self.valor.hour

    @property
    def minuto(self) -> int:
        return self.valor.minute

    @property
    def segundo(self) -> int:
        return self.valor.second

    def to_seconds(self) -> int:
        return self.hora * 3600 + self.minuto * 60 + self.segundo

    def to_time(self) -> time:
        return time(self.hora(), self.minuto(), self.segundo())

    def __lt__(self, other: object) -> bool:  # type: ignore[override]
        if not isinstance(other, HorarioDoHabito):
            return NotImplemented
        return (self.hora, self.minuto, self.segundo) < (other.hora, other.minuto, other.segundo)

    def __str__(self) -> str:
        return self.as_user()


# ------------------------------
# Validação simples
# ------------------------------

def _validate_hms(h: int, m: int, s: int) -> None:
    if not (0 <= h <= 23):
        raise ValueError(f"hora inválida: {h} (esperado 0..23)")
    if not (0 <= m <= 59):
        raise ValueError(f"minuto inválido: {m} (esperado 0..59)")
    if not (0 <= s <= 59):
        raise ValueError(f"segundo inválido: {s} (esperado 0..59)")
