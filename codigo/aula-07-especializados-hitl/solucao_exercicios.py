"""Gabarito dos laboratórios da Aula 7.

    python solucao_exercicios.py            # todos
    python solucao_exercicios.py basico
"""

from __future__ import annotations

import sys

from app import agentes, hitl
from app.bases_sinteticas import OCORRENCIAS
from app.hitl import Checkpoint, Concluido, DecisaoHumana, Fluxo, Pausado
from app.memoria import Estado


def _novo(oc_id="PCDF-SIM-0002"):
    return Estado(id=oc_id, texto=OCORRENCIAS[oc_id])


# ---------------------------------------------------------------------------
# LAB BÁSICO — um agente novo (Vitimologia) antes do Jurídico
# ---------------------------------------------------------------------------
def vitimologia(e: Estado) -> Estado:
    m = e.memoria_de("vitimologia")
    campos = (e.fatos or {}).get("campos", {})
    vulneravel = campos.get("grave_ameaca")   # exemplo didático simples
    e.hipotese = {**(e.hipotese or {}), "atencao_vitima": "prioridade de acolhimento" if vulneravel else "padrão"}
    m.anotar(f"acolhimento: {'prioridade' if vulneravel else 'padrão'}")
    e.guardar_memoria(m)
    return e


def lab_basico() -> None:
    print("== LAB BÁSICO: inserir o agente Vitimologia entre Analista e Jurídico ==")
    # a ordem do fluxo é um dict — inserir é declarar o novo passo
    hitl.ORDEM["vitimologia"] = vitimologia
    hitl.PROXIMA["analisar"] = "vitimologia"
    hitl.PROXIMA["vitimologia"] = "juridico"
    try:
        r = Fluxo().iniciar(_novo())
        r = Fluxo().retomar(r.checkpoint, DecisaoHumana(aprovado=True))
        print("  hipótese.:", r.estado.hipotese)
        print("  memórias.:", sorted(r.estado.memorias))
        assert "vitimologia" in r.estado.memorias
    finally:
        hitl.ORDEM.pop("vitimologia")
        hitl.PROXIMA["analisar"] = "juridico"
        hitl.PROXIMA.pop("vitimologia")


# ---------------------------------------------------------------------------
# LAB INTERMEDIÁRIO — o operador vê a memória de cada agente antes de decidir
# ---------------------------------------------------------------------------
def lab_intermediario() -> None:
    print("\n== LAB INTERMEDIÁRIO: painel de decisão do operador ==")
    r = Fluxo().iniciar(_novo("PCDF-SIM-0009"))
    assert isinstance(r, Pausado)
    e = Checkpoint.carregar(r.checkpoint)
    print("  PROPOSTA:", r.proposta["artigo"], "—", r.proposta["fundamento"])
    print("  para o operador decidir, mostre:")
    for agente in ("investigador", "analista", "juridico"):
        print(f"    {agente}: {e.memorias.get(agente, {}).get('notas')}")
    # decide com base nisso
    r = Fluxo().retomar(r.checkpoint, DecisaoHumana(aprovado=True, operador="escrivã"))
    assert isinstance(r, Concluido)
    print("  decidido:", r.estado.dossie["tipificacao"]["natureza"])


# ---------------------------------------------------------------------------
# DESAFIO — um segundo breakpoint (antes de "encaminhar para análise de vínculos")
# ---------------------------------------------------------------------------
def desafio() -> None:
    print("\n== DESAFIO: onde colocar um segundo ponto de parada ==")
    print("  Regra: qualquer nó cujo resultado seja usado para uma AÇÃO sobre pessoas")
    print("  (não só para organizar informação) precisa de um breakpoint antes.")
    print("  No SIGMA atual: só a tipificação. Um nó 'análise de vínculos entre")
    print("  investigados' precisaria de um 2º breakpoint — modele-o em hitl.PROXIMA")
    print("  como 'aguardando_aprovacao_vinculos' e trate no _rodar/retomar.")


LABS = {"basico": lab_basico, "intermediario": lab_intermediario, "desafio": desafio}

if __name__ == "__main__":
    alvo = sys.argv[1] if len(sys.argv) > 1 else None
    (LABS[alvo]() if alvo in LABS else [fn() for fn in LABS.values()])
