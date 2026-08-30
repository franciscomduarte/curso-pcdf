"""Gabarito dos laboratórios da Aula 6.

    python solucao_exercicios.py            # todos
    python solucao_exercicios.py basico     # um por vez
"""

from __future__ import annotations

import sys

from app import nos
from app.bases_sinteticas import OCORRENCIAS
from app.estado import Estado
from app.grafo import END, START, Grafo
from app.sigma_grafo import construir


# ---------------------------------------------------------------------------
# LAB BÁSICO — um nó novo entre classificar e consultar
# ---------------------------------------------------------------------------
def priorizar(e: Estado) -> Estado:
    e.classificacao["fila"] = "plantão" if e.classificacao["natureza"] == "Roubo" else "cartório"
    return e


def lab_basico() -> None:
    print("== LAB BÁSICO: inserir um nó 'priorizar' entre classificar e o resto ==")
    g = construir()
    g.no("priorizar", priorizar)
    # a condicional que estava em 'classificar' passa para 'priorizar';
    # 'classificar' agora vai sempre para 'priorizar' (aresta estática).
    g._condicionais["priorizar"] = g._condicionais.pop("classificar")
    g.aresta("classificar", "priorizar")
    e = g.compilar().executar(Estado(id="x", texto=OCORRENCIAS["PCDF-SIM-0002"]))
    print("  caminho:", " -> ".join(e.caminho))
    print("  fila...:", e.classificacao["fila"])
    assert e.caminho[:3] == ["extrair", "classificar", "priorizar"]


# ---------------------------------------------------------------------------
# LAB INTERMEDIÁRIO — ramos paralelos (aqui, sequenciais) e um nó de junção
# ---------------------------------------------------------------------------
def lab_intermediario() -> None:
    print("\n== LAB INTERMEDIÁRIO: dois enriquecimentos + junção ==")

    def consultar_veiculo_no(e: Estado) -> Estado:
        c = e.campos or {}
        e.enriquecimento = (e.enriquecimento or []) + [
            {"veiculo": nos.consultar_veiculo(c["placa_citada"])} if c.get("placa_citada")
            else {"veiculo": None}]
        return e

    def consultar_historico_no(e: Estado) -> Estado:
        c = e.campos or {}
        e.enriquecimento = (e.enriquecimento or []) + [
            {"historico": nos.consultar_similares(c.get("local"))}]
        return e

    def juntar(e: Estado) -> Estado:
        e.pendencias = [] if e.enriquecimento else ["nada encontrado"]
        e.revisado = True
        return e

    g = Grafo()
    g.no("extrair", nos.extrair).no("classificar", nos.classificar)
    g.no("veiculo", consultar_veiculo_no).no("historico", consultar_historico_no).no("juntar", juntar)
    g.aresta(START, "extrair").aresta("extrair", "classificar")
    g.aresta("classificar", "veiculo").aresta("veiculo", "historico").aresta("historico", "juntar")
    g.aresta("juntar", END)
    e = g.compilar().executar(Estado(id="x", texto=OCORRENCIAS["PCDF-SIM-0002"]))
    print("  caminho:", " -> ".join(e.caminho))
    print("  enriquecimento tem", len(e.enriquecimento), "partes (veículo + histórico)")
    assert len(e.enriquecimento) == 2


# ---------------------------------------------------------------------------
# DESAFIO — o grafo se valida antes de rodar
# ---------------------------------------------------------------------------
def desafio() -> None:
    print("\n== DESAFIO: validação estática pega o erro antes da execução ==")
    from app.grafo import GrafoInvalido

    g = Grafo().no("a", lambda e: e).no("b", lambda e: e)
    g.aresta(START, "a").aresta("a", "b")   # 'b' não tem saída!
    try:
        g.compilar()
    except GrafoInvalido as exc:
        print(f"  compilar() recusou: {exc}")

    # grafo do SIGMA: sem ciclo nas arestas estáticas, mas com ciclo condicional
    sigma = construir()
    print(f"  SIGMA tem_ciclo(estáticas)={sigma.tem_ciclo()} — o ciclo real é a condicional revisar->consultar")


LABS = {"basico": lab_basico, "intermediario": lab_intermediario, "desafio": desafio}

if __name__ == "__main__":
    alvo = sys.argv[1] if len(sys.argv) > 1 else None
    (LABS[alvo]() if alvo in LABS else [fn() for fn in LABS.values()])
