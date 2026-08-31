"""Gabarito dos laboratórios da Aula 9.

    python solucao_exercicios.py
    python solucao_exercicios.py basico
    python solucao_exercicios.py intermediario
    python solucao_exercicios.py desafio
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass

from app.agentes import analista, consolidador, investigador, juridico
from app.autoscaler import HPA, avaliar
from app.bases_sinteticas import BOLETIM_SUSPEITO, OCORRENCIAS
from app.cluster import Cluster, ServicoIndisponivel
from app.fluxo import Fluxo
from app.guardrail import EntradaRejeitada, Guardrail, TaxaExcedida, gate
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


# ===========================================================================
# EXERCÍCIOS EXTRAS (se sobrar tempo) — referência
# ===========================================================================

# --- Extra 1: janela de estabilização evita flapping do HPA (avançado) -----
@dataclass
class EstadoEstabilizacao:
    """Guarda quando foi o último scale-down, para a janela de estabilização."""
    ultimo_scale_down_em: float | None = None


def avaliar_com_estabilizacao(cluster: Cluster, hpa: HPA, carga_atual: float,
                               agora: float, estab: EstadoEstabilizacao,
                               janela_estabilizacao_s: float = 60.0) -> dict:
    """Como avaliar(), mas RECUSA reduzir réplicas se faz menos de
    `janela_estabilizacao_s` do último scale-down. É o
    `stabilizationWindowSeconds` que o HPA real usa por padrão no scaleDown
    (Bloco 7) — evita o 'flapping' quando a carga oscila em torno do alvo.
    Scale-UP nunca é bloqueado (subir rápido é o comportamento seguro)."""
    dep = cluster.deployments[hpa.deployment]
    antes = dep.replicas
    if carga_atual <= 0:
        desejadas = hpa.min_replicas
    else:
        desejadas = math.ceil(antes * (carga_atual / hpa.alvo_por_pod))
    desejadas = max(hpa.min_replicas, min(hpa.max_replicas, desejadas))

    if desejadas < antes:   # scale-down: checa a janela
        ultimo = estab.ultimo_scale_down_em
        if ultimo is not None and (agora - ultimo) < janela_estabilizacao_s:
            return {"hpa": hpa.nome, "replicas_antes": antes, "replicas_depois": antes,
                    "bloqueado_por_estabilizacao": True}
        estab.ultimo_scale_down_em = agora

    if desejadas != antes:
        cluster.escalar(hpa.deployment, desejadas)
    return {"hpa": hpa.nome, "replicas_antes": antes, "replicas_depois": desejadas,
            "bloqueado_por_estabilizacao": False}


def extra_flapping() -> None:
    print("== EXTRA 1: janela de estabilização evita flapping do HPA ==")
    sequencia = [("t=0", 0.0, 9.0), ("t=10", 10.0, 2.0), ("t=20", 20.0, 9.0),
                 ("t=30", 30.0, 2.0), ("t=90", 90.0, 2.0)]
    hpa = HPA(nome="h", deployment="investigador-deploy", alvo_por_pod=3.0,
              min_replicas=1, max_replicas=6)

    print("  SEM estabilização (avaliar padrão):")
    c1 = _cluster_sigma()
    for rot, _agora, carga in sequencia:
        r = avaliar(c1, hpa, carga)
        print(f"    {rot:<5} carga={carga:>4.1f} -> {r['replicas_antes']} -> {r['replicas_depois']}")

    print("  COM estabilização de 60s no scale-down:")
    c2 = _cluster_sigma()
    estab = EstadoEstabilizacao()
    for rot, agora, carga in sequencia:
        r = avaliar_com_estabilizacao(c2, hpa, carga, agora, estab, janela_estabilizacao_s=60.0)
        marca = "  (scale-down bloqueado)" if r["bloqueado_por_estabilizacao"] else ""
        print(f"    {rot:<5} carga={carga:>4.1f} -> {r['replicas_antes']} -> {r['replicas_depois']}{marca}")


# --- Extra 2: guardrail observável — contador de bloqueios por origem ------
def gate_contando(guardrail: Guardrail, contador: dict, origem: str, texto: str) -> bool:
    """Como gate(), mas conta os bloqueios por origem em `contador` em vez de
    deixar a exceção subir. Devolve True se passou, False se foi barrado."""
    try:
        gate(guardrail, origem, texto)
        return True
    except (EntradaRejeitada, TaxaExcedida):
        contador[origem] = contador.get(origem, 0) + 1
        return False


def painel_guardrail(contador: dict) -> str:
    linhas = [f"{'ORIGEM':<20} {'BLOQUEIOS':>10}"]
    for origem, n in sorted(contador.items(), key=lambda kv: (-kv[1], kv[0])):
        linhas.append(f"{origem:<20} {n:>10}")
    return "\n".join(linhas)


def extra_guardrail_observavel() -> None:
    print("\n== EXTRA 2: guardrail observável — quem mais bate na porta ==")
    g = Guardrail(limite_por_janela=2, janela_s=60.0)
    contador: dict[str, int] = {}

    for _ in range(4):   # legítima, mas estoura a cota de 2 -> 2 bloqueios
        gate_contando(g, contador, "delegacia-01", "furto simples sem testemunhas")
    for _ in range(3):   # injeção -> 3 bloqueios
        gate_contando(g, contador, "fonte-desconhecida", BOLETIM_SUSPEITO)
    gate_contando(g, contador, "delegacia-02", "veículo abandonado na via")   # ok, 0 bloqueio

    print(painel_guardrail(contador))
    print("  bloqueio não é só 'negar' — é sinal: a origem no topo da lista merece atenção.")


def extras() -> None:
    extra_flapping()
    extra_guardrail_observavel()


LABS = {
    "basico": lab_basico,
    "intermediario": lab_intermediario,
    "desafio": desafio,
    "extras": extras,
}

if __name__ == "__main__":
    alvo = sys.argv[1] if len(sys.argv) > 1 else None
    if alvo in LABS:
        LABS[alvo]()
    else:
        for fn in LABS.values():
            fn()
