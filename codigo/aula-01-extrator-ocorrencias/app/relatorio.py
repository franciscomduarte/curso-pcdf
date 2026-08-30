"""Desafio avançado: consolidação de várias ocorrências.

Recebe uma lista de Ocorrencia e devolve um resumo agregado: contagem por
natureza, por região e a fila de casos que precisam de revisão humana.
"""

from __future__ import annotations

from collections import Counter

from .classificador import classificar
from .esquema import Ocorrencia


def consolidar(ocorrencias: list[Ocorrencia]) -> dict:
    por_natureza = Counter(o.natureza.value for o in ocorrencias)
    por_regiao = Counter(o.local or "não informado" for o in ocorrencias)

    revisar = []
    for indice, ocorrencia in enumerate(ocorrencias):
        c = classificar(ocorrencia)
        if c.revisar:
            revisar.append({"indice": indice, "motivo": c.motivo})

    return {
        "total": len(ocorrencias),
        "por_natureza": dict(por_natureza.most_common()),
        "por_regiao": dict(por_regiao.most_common()),
        "para_revisao_humana": revisar,
    }


def formatar(relatorio: dict) -> str:
    linhas = [f"Total de ocorrências: {relatorio['total']}", "", "Por natureza:"]
    linhas += [f"  {k:.<28} {v}" for k, v in relatorio["por_natureza"].items()]
    linhas += ["", "Por região administrativa:"]
    linhas += [f"  {k:.<28} {v}" for k, v in relatorio["por_regiao"].items()]
    linhas += ["", f"Para revisão humana: {len(relatorio['para_revisao_humana'])}"]
    linhas += [f"  #{r['indice']}: {r['motivo']}" for r in relatorio["para_revisao_humana"]]
    return "\n".join(linhas)
