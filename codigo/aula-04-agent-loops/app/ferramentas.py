"""As ferramentas que o loop pode acionar.

Cada uma declara um `custo` (unidades fictícias — imite "tokens" ou "chamadas
pagas") que o orçamento do loop vai consumindo. `ferramenta_instavel` falha as
duas primeiras vezes de propósito, para exercitar o retry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .bases_sinteticas import DOCUMENTOS, OCORRENCIAS_HISTORICO, VEICULOS


@dataclass
class Ferramenta:
    nome: str
    descricao: str
    funcao: Callable[..., object]
    custo: int = 1
    sensivel: bool = False


def consultar_veiculo(placa: str) -> dict:
    d = VEICULOS.get(placa.strip().upper())
    return {"placa": placa.upper(), "encontrado": bool(d), **(d or {})}


def consultar_ocorrencias_similares(regiao: str, natureza: str = "Furto") -> list[dict]:
    r, n = regiao.strip().lower(), natureza.strip().lower()
    return [o for o in OCORRENCIAS_HISTORICO
            if o["regiao"].lower() == r and o["natureza"].lower() == n]


def buscar_documento(assunto: str) -> list[dict]:
    a = assunto.strip().lower()
    return [d for d in DOCUMENTOS if a in d["assunto"].lower() or a in d["trecho"].lower()]


def montar_linha_tempo(eventos: str) -> dict:
    """'Sintetiza' — recebe os eventos coletados como texto e devolve uma timeline."""
    linhas = [e.strip(" -•\t") for e in eventos.splitlines() if e.strip()]
    return {"linha_do_tempo": linhas, "total_eventos": len(linhas)}


class _Instavel:
    def __init__(self) -> None:
        self.tentativas = 0

    def __call__(self, recurso: str) -> dict:
        self.tentativas += 1
        if self.tentativas <= 2:
            raise ConnectionError("serviço externo temporariamente indisponível (simulado)")
        return {"recurso": recurso, "status": "ok após retry", "tentativas": self.tentativas}


REGISTRO: dict[str, Ferramenta] = {
    "consultar_veiculo": Ferramenta(
        "consultar_veiculo", "Consulta uma placa. Args: placa.",
        consultar_veiculo, custo=2, sensivel=True),
    "consultar_ocorrencias_similares": Ferramenta(
        "consultar_ocorrencias_similares",
        "Ocorrências da mesma região/natureza. Args: regiao, natureza.",
        consultar_ocorrencias_similares, custo=2),
    "buscar_documento": Ferramenta(
        "buscar_documento", "Busca documentos por assunto. Args: assunto.",
        buscar_documento, custo=1),
    "montar_linha_tempo": Ferramenta(
        "montar_linha_tempo", "Sintetiza os eventos coletados. Args: eventos (texto).",
        montar_linha_tempo, custo=3),
    "servico_externo": Ferramenta(
        "servico_externo", "Consulta um serviço externo instável. Args: recurso.",
        _Instavel(), custo=1),
}
