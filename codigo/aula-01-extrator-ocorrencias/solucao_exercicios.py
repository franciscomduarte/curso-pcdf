"""Gabarito dos laboratórios da Aula 1.

    python solucao_exercicios.py

Contém as soluções de referência. Use em sala só depois que a turma tentar.
"""

from __future__ import annotations

import re

from pydantic import Field

from app.classificador import classificar
from app.dados_sinteticos import OCORRENCIAS_BRUTAS
from app.esquema import Ocorrencia
from app.llm import MockExtrator
from app.relatorio import consolidar, formatar


# ---------------------------------------------------------------------------
# LAB BÁSICO — novo campo `objetos_subtraidos`
# ---------------------------------------------------------------------------
class OcorrenciaComSubtraidos(Ocorrencia):
    """Estende o esquema com a lista de itens efetivamente levados."""

    objetos_subtraidos: list[str] = Field(default_factory=list)


class MockComSubtraidos(MockExtrator):
    """Mesma heurística; separa os objetos ligados a verbos de subtração."""

    def extrair(self, texto: str) -> OcorrenciaComSubtraidos:  # type: ignore[override]
        base = super().extrair(texto)
        subtraidos = []
        if re.search(r"subtra|levaram|furtad|assalt", texto, re.I):
            subtraidos = base.objetos
        return OcorrenciaComSubtraidos(
            **base.model_dump(), objetos_subtraidos=subtraidos
        )


def lab_basico() -> None:
    print("== LAB BÁSICO: campo objetos_subtraidos ==")
    llm = MockComSubtraidos()
    oc = llm.extrair(OCORRENCIAS_BRUTAS[0]["texto"])
    print("objetos.............:", oc.objetos)
    print("objetos_subtraidos..:", oc.objetos_subtraidos)


# ---------------------------------------------------------------------------
# LAB INTERMEDIÁRIO — classificação + fila de revisão
# ---------------------------------------------------------------------------
def lab_intermediario() -> None:
    print("\n== LAB INTERMEDIÁRIO: classificação ==")
    llm = MockExtrator()
    for item in OCORRENCIAS_BRUTAS:
        oc = llm.extrair(item["texto"])
        c = classificar(oc)
        marca = "REVISAR" if c.revisar else "ok"
        print(f"  {item['id']}: {c.natureza.value:<14} [{marca}] {c.motivo}")


# ---------------------------------------------------------------------------
# DESAFIO AVANÇADO — relatório consolidado
# ---------------------------------------------------------------------------
def desafio_avancado() -> None:
    print("\n== DESAFIO AVANÇADO: relatório consolidado ==")
    llm = MockExtrator()
    ocorrencias = [llm.extrair(i["texto"]) for i in OCORRENCIAS_BRUTAS]
    print(formatar(consolidar(ocorrencias)))


if __name__ == "__main__":
    lab_basico()
    lab_intermediario()
    desafio_avancado()
