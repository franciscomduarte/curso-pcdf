"""Nível intermediário: o ciclo e a trava.

    python main_ciclo.py

Mostra:
  1. um grafo DAG (sem volta) — termina sempre
  2. o grafo do SIGMA com a condicional que volta — termina porque o roteador
     tem condição de saída (tentativas < MAX)
  3. um grafo com ciclo SEM condição de saída — só a trava de passos o segura
"""

from __future__ import annotations

from app.bases_sinteticas import AVISO_DADOS, OCORRENCIAS
from app.estado import Estado
from app.grafo import END, START, Grafo
from app.sigma_grafo import construir


def dag() -> None:
    print("\n1) DAG — extrair -> classificar -> revisar -> END (sem volta)")
    g = Grafo()
    from app import nos
    g.no("extrair", nos.extrair).no("classificar", nos.classificar).no("revisar", nos.revisar)
    g.aresta(START, "extrair").aresta("extrair", "classificar")
    g.aresta("classificar", "revisar").aresta("revisar", END)
    print("   tem_ciclo():", g.tem_ciclo())
    e = g.compilar().executar(Estado(id="x", texto=OCORRENCIAS["PCDF-SIM-0002"]))
    print("   caminho:", " -> ".join(e.caminho), f"({e.passos} passos)")


def sigma_com_ciclo() -> None:
    print("\n2) SIGMA — revisar volta a consultar UMA vez, depois encerra")
    e = construir().compilar().executar(Estado(id="x", texto=OCORRENCIAS["PCDF-SIM-0009"]))
    print("   caminho:", " -> ".join(e.caminho), f"({e.passos} passos)")
    print("   (consultar aparece 2x: 1a busca por região, 2a busca ampla)")


def ciclo_sem_saida() -> None:
    print("\n3) ciclo SEM condição de saída — a trava de passos segura")
    g = Grafo()
    g.no("a", lambda e: e).no("b", lambda e: e)
    g.aresta(START, "a").aresta("a", "b").aresta("b", "a")   # a <-> b para sempre
    print("   tem_ciclo():", g.tem_ciclo())
    e = g.compilar(max_passos=8).executar(Estado(id="x", texto="..."))
    print("   caminho:", " -> ".join(e.caminho))
    print("   pendências:", e.pendencias)


def main() -> None:
    print(f"* {AVISO_DADOS}")
    dag()
    sigma_com_ciclo()
    ciclo_sem_saida()


if __name__ == "__main__":
    main()
