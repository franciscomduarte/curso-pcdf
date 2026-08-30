"""Nível básico: roda o grafo do SIGMA e mostra o caminho percorrido.

    python main.py                 # PCDF-SIM-0009 (dispara o ciclo)
    python main.py PCDF-SIM-0002
    python main.py PCDF-SIM-0011   # relato confuso -> desvio para o humano
"""

from __future__ import annotations

import sys

from app.bases_sinteticas import AVISO_DADOS, OCORRENCIAS
from app.estado import Estado
from app.sigma_grafo import construir


def main() -> None:
    print(f"* {AVISO_DADOS}\n")
    oc_id = sys.argv[1] if len(sys.argv) > 1 else "PCDF-SIM-0009"

    grafo = construir()
    print(f"grafo tem ciclo (arestas estáticas)? {grafo.tem_ciclo()}  "
          f"(o ciclo real está nas condicionais)\n")

    app = grafo.compilar(max_passos=25)
    e = app.executar(Estado(id=oc_id, texto=OCORRENCIAS[oc_id]))

    print(f"ocorrência: {oc_id}")
    print("caminho...:", " -> ".join(e.caminho))
    print("passos....:", e.passos)
    print("natureza..:", e.classificacao and e.classificacao["natureza"])
    print("enriquec..:", e.enriquecimento)
    print("pendências:", e.pendencias or "nenhuma")


if __name__ == "__main__":
    main()
