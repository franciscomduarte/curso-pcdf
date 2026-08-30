"""Laboratório intermediário: classificação da natureza da ocorrência.

Reaproveita o extrator: a natureza já vem no objeto Ocorrencia. Aqui só
isolamos essa responsabilidade e adicionamos uma checagem de confiança
simples (heurística) para sinalizar casos que merecem revisão humana.
"""

from __future__ import annotations

from dataclasses import dataclass

from .esquema import NaturezaOcorrencia, Ocorrencia


@dataclass
class Classificacao:
    natureza: NaturezaOcorrencia
    revisar: bool
    motivo: str


def classificar(ocorrencia: Ocorrencia) -> Classificacao:
    # Sinais de baixa confiança -> encaminhar para triagem humana.
    if ocorrencia.natureza == NaturezaOcorrencia.OUTROS:
        return Classificacao(ocorrencia.natureza, True, "natureza não reconhecida")
    if not ocorrencia.local or not ocorrencia.data_fato:
        return Classificacao(ocorrencia.natureza, True, "faltam data ou local")
    if len(ocorrencia.resumo) < 20:
        return Classificacao(ocorrencia.natureza, True, "resumo muito curto")
    return Classificacao(ocorrencia.natureza, False, "campos mínimos presentes")
