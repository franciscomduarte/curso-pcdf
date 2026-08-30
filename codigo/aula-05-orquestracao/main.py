"""Nível básico: roda UM padrão e mostra o dossiê + as métricas.

    python main.py                 # supervisor, por padrão
    python main.py pipeline
    python main.py blackboard PCDF-SIM-0009
"""

from __future__ import annotations

import sys

from dotenv import load_dotenv

from app import padroes
from app.bases_sinteticas import AVISO_DADOS, OCORRENCIAS
from app.especialistas import Dossie
from app.llm import llm_padrao


def main() -> None:
    load_dotenv()
    print(f"* {AVISO_DADOS}\n")

    nome = sys.argv[1] if len(sys.argv) > 1 else "supervisor"
    oc_id = sys.argv[2] if len(sys.argv) > 2 else "PCDF-SIM-0002"
    d = Dossie(id=oc_id, texto=OCORRENCIAS[oc_id])

    if nome == "pipeline":
        d, m = padroes.pipeline(d)
    elif nome == "supervisor":
        d, m = padroes.supervisor(d, llm_padrao())
    elif nome == "broker":
        d, m = padroes.broker(d)
    elif nome == "blackboard":
        d, m = padroes.blackboard(d)
    else:
        raise SystemExit("padrões: pipeline | supervisor | broker | blackboard")

    print(f"padrão: {nome}   ocorrência: {oc_id}\n")
    print("campos.........:", d.campos)
    print("classificação..:", d.classificacao)
    print("enriquecimento.:", d.enriquecimento)
    print("pendências.....:", d.pendencias or "nenhuma")
    print("completo.......:", d.completo)
    print("\n" + m.linha())


if __name__ == "__main__":
    main()
