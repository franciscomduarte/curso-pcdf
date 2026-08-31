"""Gabarito dos laboratórios da Aula 9.

    python solucao_exercicios.py
    python solucao_exercicios.py basico
    python solucao_exercicios.py intermediario
    python solucao_exercicios.py desafio
"""

from __future__ import annotations

import sys

from app.agentes import analista, consolidador, investigador, juridico
from app.autoscaler import HPA, avaliar
from app.bases_sinteticas import OCORRENCIAS
from app.cluster import Cluster, ServicoIndisponivel
from app.fluxo import Fluxo
from app.guardrail import Guardrail
from app.memoria import Estado
from app.observabilidade import Metricas
from app.store import StoreCompartilhado


def _cluster_sigma(metricas: Metricas | None = None) -> Cluster:
    c = Cluster(metricas=metricas or Metricas())
    c.criar_deployment("investigador-deploy", investigador, replicas=1)
    c.criar_deployment("analista-deploy", analista, replicas=1)
    c.criar_deployment("juridico-deploy", juridico, replicas=1)
    c.criar_deployment("consolidador-deploy", consolidador, replicas=1)
    c.criar_service("investigador-svc", "investigador-deploy")
    c.criar_service("analista-svc", "analista-deploy")
    c.criar_service("juridico-svc", "juridico-deploy")
    c.criar_service("consolidador-svc", "consolidador-deploy")
    return c


# ---------------------------------------------------------------------------
# LAB BÁSICO — o HPA nunca sai de [min, max], mesmo com carga extrema
# ---------------------------------------------------------------------------
def lab_basico() -> None:
    print("== LAB BÁSICO: HPA respeita min/max mesmo em carga extrema ==")
    c = _cluster_sigma()
    hpa = HPA(nome="investigador-hpa", deployment="investigador-deploy",
              alvo_por_pod=3.0, min_replicas=1, max_replicas=4)

    for carga in (2.0, 50.0, 100.0, 0.0, 4.0):
        r = avaliar(c, hpa, carga)
        print(f"  carga={carga:>6.1f} -> {r['replicas_antes']} -> {r['replicas_depois']} "
              f"(dentro de [{hpa.min_replicas}, {hpa.max_replicas}]? "
              f"{hpa.min_replicas <= r['replicas_depois'] <= hpa.max_replicas})")


# ---------------------------------------------------------------------------
# LAB INTERMEDIÁRIO — diagnosticar (repete o cenário de main_incidente.py de
# forma programática) + guardrail em duas origens independentes
# ---------------------------------------------------------------------------
def lab_intermediario() -> None:
    print("\n== LAB INTERMEDIÁRIO (1): o painel aponta o serviço doente ==")
    metricas = Metricas()
    c = _cluster_sigma(metricas)
    fluxo = Fluxo(c, StoreCompartilhado())

    fluxo.iniciar(Estado(id="PCDF-SIM-0002", texto=OCORRENCIAS["PCDF-SIM-0002"]))
    c.matar_pod("juridico-deploy", 0)
    for oc_id in ("PCDF-SIM-0009", "PCDF-SIM-0015"):
        try:
            fluxo.iniciar(Estado(id=oc_id, texto=OCORRENCIAS[oc_id]))
        except ServicoIndisponivel:
            pass

    pior = max(metricas.chamadas, key=lambda s: metricas.taxa_de_erro(s))
    print(f"  serviço com maior taxa de erro: {pior} ({metricas.taxa_de_erro(pior) * 100:.0f}%)")

    c.reconciliar()
    r = fluxo.iniciar(Estado(id="PCDF-SIM-0002", texto=OCORRENCIAS["PCDF-SIM-0002"]))
    print(f"  depois de reconciliar(): nova tentativa {'OK' if r else 'falhou'}")

    print("\n== LAB INTERMEDIÁRIO (2): guardrail — origens não compartilham cota ==")
    g = Guardrail(limite_por_janela=2, janela_s=60.0)
    resultado_a = [g.permitir("origem-A") for _ in range(3)]
    resultado_b = [g.permitir("origem-B") for _ in range(3)]
    print(f"  origem-A (limite 2): {resultado_a}")
    print(f"  origem-B (limite 2, independente): {resultado_b}")


# ---------------------------------------------------------------------------
# DESAFIO — alertas a partir do painel de métricas
# ---------------------------------------------------------------------------
def verificar_alertas(metricas: Metricas, limiar_erro: float = 0.5,
                       limiar_p95_ms: float = 500.0) -> list[str]:
    """Varre o painel e devolve uma lista de alertas — nenhuma mágica: só
    comparar número com limiar, para cada serviço que já recebeu chamada."""
    alertas = []
    for servico in sorted(metricas.chamadas):
        taxa = metricas.taxa_de_erro(servico)
        if taxa >= limiar_erro:
            alertas.append(f"ALERTA taxa de erro: {servico} em {taxa * 100:.0f}% "
                           f"(limiar {limiar_erro * 100:.0f}%)")
        p95 = metricas.latencia_p95_ms(servico)
        if p95 >= limiar_p95_ms:
            alertas.append(f"ALERTA latência p95: {servico} em {p95:.0f}ms "
                           f"(limiar {limiar_p95_ms:.0f}ms)")
    return alertas


def desafio() -> None:
    print("\n== DESAFIO: alertas automáticos a partir do painel ==")
    metricas = Metricas()
    c = _cluster_sigma(metricas)
    fluxo = Fluxo(c, StoreCompartilhado())

    fluxo.iniciar(Estado(id="PCDF-SIM-0002", texto=OCORRENCIAS["PCDF-SIM-0002"]))
    c.matar_pod("juridico-deploy", 0)
    for _ in range(3):
        try:
            fluxo.iniciar(Estado(id="PCDF-SIM-0009", texto=OCORRENCIAS["PCDF-SIM-0009"]))
        except ServicoIndisponivel:
            pass

    for alerta in verificar_alertas(metricas):
        print(f"  {alerta}")
    print(f"  ({len(verificar_alertas(metricas))} alerta(s) — 0 seria um cluster saudável)")


LABS = {
    "basico": lab_basico,
    "intermediario": lab_intermediario,
    "desafio": desafio,
}

if __name__ == "__main__":
    alvo = sys.argv[1] if len(sys.argv) > 1 else None
    if alvo in LABS:
        LABS[alvo]()
    else:
        for fn in LABS.values():
            fn()
