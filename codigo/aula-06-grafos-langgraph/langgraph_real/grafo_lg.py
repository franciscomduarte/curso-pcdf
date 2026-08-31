"""O MESMO grafo do SIGMA, agora com o LangGraph.

    pip install -r ../requirements-opcionais.txt
    python langgraph_real/grafo_lg.py

Diferenças em relação ao motor mínimo (app/grafo.py):
  - o estado é um TypedDict; cada nó devolve só as CHAVES que mudou, e o
    LangGraph faz o merge (não é preciso devolver o estado inteiro);
  - `add_conditional_edges(no, roteador, {rótulo: destino})` — o roteador
    devolve um rótulo, o dicionário mapeia rótulo -> nó;
  - `recursion_limit` é a trava de passos (equivale ao nosso max_passos).

A API do LangGraph muda entre versões maiores; revalidado com langgraph 1.2.11
(2026-08). `requirements-opcionais.txt` pina `langgraph>=1.0,<2`.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from langgraph.graph import END, START, StateGraph
except ImportError as exc:  # noqa: BLE001
    raise SystemExit(f"LangGraph não encontrado ({exc}). pip install -r requirements-opcionais.txt")

from app.bases_sinteticas import (  # noqa: E402
    OCORRENCIAS, consultar_similares, consultar_veiculo, extrair_campos,
)


class EstadoSIGMA(TypedDict, total=False):
    id: str
    texto: str
    campos: dict
    classificacao: dict
    enriquecimento: list
    pendencias: list
    tentativas: int
    caminho: Annotated[list, lambda a, b: a + b]   # reducer: concatena


def extrair(s):
    return {"campos": extrair_campos(s["texto"]), "caminho": ["extrair"]}


def classificar(s):
    natureza = "Roubo" if s["campos"].get("tem_violencia") else "Furto"
    return {"classificacao": {"natureza": natureza}, "caminho": ["classificar"]}


def consultar(s):
    c, tent = s["campos"], s.get("tentativas", 0)
    achados = []
    if c.get("placa_citada"):
        achados.append(consultar_veiculo(c["placa_citada"]))
    achados.append({"similares": consultar_similares(
        c.get("local"), s["classificacao"]["natureza"], ampla=tent >= 1)})
    return {"enriquecimento": achados, "tentativas": tent + 1, "caminho": ["consultar"]}


def revisar(s):
    util = any(i.get("similares") or str(i.get("situacao", "")).startswith("consta")
               for i in s.get("enriquecimento", []))
    pend = [] if util else ["enriquecimento sem resultado"]
    return {"pendencias": pend, "caminho": ["revisar"]}


def encaminhar_humano(s):
    return {"pendencias": ["ENVIADO para triagem humana"], "caminho": ["encaminhar_humano"]}


def rota_classificar(s):
    return "humano" if s["campos"].get("confuso") else "consultar"


def rota_revisar(s):
    if s["pendencias"] and s.get("tentativas", 0) < 2:
        return "repetir"
    return "fim"


def construir():
    g = StateGraph(EstadoSIGMA)
    for nome, fn in [("extrair", extrair), ("classificar", classificar),
                     ("consultar", consultar), ("revisar", revisar),
                     ("encaminhar_humano", encaminhar_humano)]:
        g.add_node(nome, fn)
    g.add_edge(START, "extrair")
    g.add_edge("extrair", "classificar")
    g.add_conditional_edges("classificar", rota_classificar,
                            {"consultar": "consultar", "humano": "encaminhar_humano"})
    g.add_edge("consultar", "revisar")
    g.add_conditional_edges("revisar", rota_revisar, {"repetir": "consultar", "fim": END})
    g.add_edge("encaminhar_humano", END)
    return g.compile()


def main() -> None:
    oc_id = sys.argv[1] if len(sys.argv) > 1 else "PCDF-SIM-0009"
    app = construir()
    final = app.invoke({"id": oc_id, "texto": OCORRENCIAS[oc_id], "caminho": []},
                       {"recursion_limit": 25})
    print(f"ocorrência: {oc_id}")
    print("caminho...:", " -> ".join(final["caminho"]))
    print("natureza..:", final["classificacao"]["natureza"])
    print("pendências:", final.get("pendencias") or "nenhuma")


if __name__ == "__main__":
    main()
