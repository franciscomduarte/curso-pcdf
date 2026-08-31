"""Gabarito dos laboratórios da Aula 10.

    python solucao_exercicios.py
    python solucao_exercicios.py basico
    python solucao_exercicios.py intermediario
    python solucao_exercicios.py desafio
"""

from __future__ import annotations

import sys

from app.agentes import analista, consolidador, investigador, juridico, revisor_dupla
from app.bases_sinteticas import OCORRENCIAS
from app.cluster import Cluster
from app.fluxo import Fluxo
from app.guardrail import EntradaRejeitada, Guardrail
from app.memoria import Estado
from app.observabilidade import Metricas
from app.store import DecisaoHumana, Pausado, StoreCompartilhado

# Mapa "quem introduziu o quê" — usado só pelo lab básico, para reforçar de
# onde cada peça do SIGMA completo vem.
ORIGEM_DA_ETAPA = {
    "investigar": "Aula 7 (papel único) rodando como Service — Aula 8",
    "analisar": "Aula 7 (papel único) rodando como Service — Aula 8",
    "juridico": "Aula 7 (breakpoint HITL) rodando como Service — Aula 8",
    "revisar": "NOVO na Aula 10 — aresta condicional da Aula 6, escalando um caso grave",
    "consolidar": "Aula 7 (dossiê final), depois da aprovação humana",
}


def _cluster_sigma(metricas: Metricas | None = None) -> Cluster:
    c = Cluster(metricas=metricas or Metricas())
    c.criar_deployment("investigador-deploy", investigador, replicas=1)
    c.criar_deployment("analista-deploy", analista, replicas=1)
    c.criar_deployment("juridico-deploy", juridico, replicas=1)
    c.criar_deployment("revisor-deploy", revisor_dupla, replicas=1)
    c.criar_deployment("consolidador-deploy", consolidador, replicas=1)
    for base in ("investigador", "analista", "juridico", "revisor", "consolidador"):
        c.criar_service(f"{base}-svc", f"{base}-deploy")
    return c


# ---------------------------------------------------------------------------
# LAB BÁSICO — mapear cada hop do traço à aula que o introduziu
# ---------------------------------------------------------------------------
def lab_basico() -> None:
    print("== LAB BÁSICO: de onde vem cada etapa do traço ==")
    fluxo = Fluxo(_cluster_sigma(), StoreCompartilhado())
    r = fluxo.iniciar(Estado(id="PCDF-SIM-0002", texto=OCORRENCIAS["PCDF-SIM-0002"]))
    assert isinstance(r, Pausado)
    e = fluxo.store.carregar(r.checkpoint)
    for passo in e.atendido_por:
        print(f"  {passo['etapa']:<10} -> {ORIGEM_DA_ETAPA[passo['etapa']]}")


# ---------------------------------------------------------------------------
# LAB INTERMEDIÁRIO — estender a aresta condicional + diagnosticar degradação
# parcial (só o Revisor cai, não o cluster inteiro)
# ---------------------------------------------------------------------------
def lab_intermediario() -> None:
    print("== LAB INTERMEDIÁRIO (1): nova aresta — veículo alertado também escala ==")
    texto = ("20/08/2026, Taguatinga. Furto de bicicleta relatado pelo comunicante. "
             "Placa citada por testemunha: ABC1D23.")

    fluxo1 = Fluxo(_cluster_sigma(), StoreCompartilhado())
    r1 = fluxo1.iniciar(Estado(id="LAB-ANTES", texto=texto))
    e1 = fluxo1.store.carregar(r1.checkpoint)
    print(f"  ANTES (aresta original):  {' -> '.join(p['etapa'] for p in e1.atendido_por)}")

    import app.roteador as roteador_mod
    original = roteador_mod.ROTEADORES_CONDICIONAIS["juridico"]

    def decidir_estendido(e: Estado) -> str:
        proposta = e.tipificacao_proposta or {}
        veiculo = (e.fatos or {}).get("veiculo") or {}
        grave = proposta.get("natureza") == "Roubo"
        veiculo_alertado = str(veiculo.get("situacao", "")).startswith("consta")
        return roteador_mod.ETAPA_REVISAO if (grave or veiculo_alertado) else roteador_mod.ETAPA_APROVACAO

    roteador_mod.ROTEADORES_CONDICIONAIS["juridico"] = decidir_estendido
    try:
        fluxo2 = Fluxo(_cluster_sigma(), StoreCompartilhado())
        r2 = fluxo2.iniciar(Estado(id="LAB-DEPOIS", texto=texto))
        e2 = fluxo2.store.carregar(r2.checkpoint)
        print(f"  DEPOIS (aresta estendida): {' -> '.join(p['etapa'] for p in e2.atendido_por)}")
    finally:
        roteador_mod.ROTEADORES_CONDICIONAIS["juridico"] = original   # nunca deixe o monkeypatch vazar

    print("\n== LAB INTERMEDIÁRIO (2): o Revisor cai — só os casos graves sentem ==")
    from app.cluster import ServicoIndisponivel
    metricas = Metricas()
    c = _cluster_sigma(metricas)
    fluxo3 = Fluxo(c, StoreCompartilhado())
    c.matar_pod("revisor-deploy", 0)

    for oc_id in ("PCDF-SIM-0002", "PCDF-SIM-0009"):   # um Roubo (usa o Revisor), um Furto (não usa)
        try:
            fluxo3.iniciar(Estado(id=oc_id, texto=OCORRENCIAS[oc_id]))
            print(f"  {oc_id}: OK")
        except ServicoIndisponivel:
            print(f"  {oc_id}: FALHOU (precisava do Revisor, que está fora do ar)")
    print(f"  painel: revisor-svc erro={metricas.taxa_de_erro('revisor-svc') * 100:.0f}%, "
          f"juridico-svc erro={metricas.taxa_de_erro('juridico-svc') * 100:.0f}% "
          "— o Furto nem chega a notar o incidente")


# ---------------------------------------------------------------------------
# DESAFIO — sintetizar métricas + roteamento + guardrail num relatório único
# ---------------------------------------------------------------------------
def gerar_relatorio_operacional(metricas: Metricas, total_processadas: int,
                                 total_revisao_dupla: int, total_barrados_guardrail: int) -> str:
    """Combina as três fontes de sinal da aula (métricas, roteamento,
    guardrail) num relatório único — nenhuma delas sozinha conta a história
    inteira de uma operação."""
    pct_revisao = (total_revisao_dupla / total_processadas * 100) if total_processadas else 0.0
    alertas = [s for s in sorted(metricas.chamadas) if metricas.taxa_de_erro(s) >= 0.5]

    linhas = [
        "RELATÓRIO OPERACIONAL — SIGMA",
        f"  ocorrências processadas: {total_processadas}",
        f"  com revisão dupla: {total_revisao_dupla} ({pct_revisao:.0f}% do lote)",
        f"  barradas pelo guardrail na entrada: {total_barrados_guardrail}",
        "",
        "  painel de métricas:",
    ]
    linhas += [f"    {linha}" for linha in metricas.painel().splitlines()]
    linhas.append("")
    linhas.append(f"  serviços em alerta (taxa de erro >= 50%): {', '.join(alertas) if alertas else 'nenhum'}")
    return "\n".join(linhas)


def desafio() -> None:
    print("== DESAFIO: relatório operacional a partir da Operação Vetor ==")
    metricas = Metricas()
    cluster = _cluster_sigma(metricas)
    gateway_guardrail = Guardrail(limite_por_janela=10)
    from app.gateway import Gateway
    gateway = Gateway(Fluxo(cluster, StoreCompartilhado()), gateway_guardrail)

    lote = ["PCDF-SIM-0002", "PCDF-SIM-0009", "PCDF-SIM-0015", "PCDF-SIM-0021"]
    revisados = 0
    for i, oc_id in enumerate(lote):
        r = gateway.processar(oc_id, OCORRENCIAS[oc_id], origem=f"delegacia-{i:02d}")
        r2 = gateway.fluxo.retomar(r.checkpoint, DecisaoHumana(aprovado=True, operador="mutirão"))
        if "revisar" in [p["etapa"] for p in r2.estado.atendido_por]:
            revisados += 1

    from app.bases_sinteticas import BOLETIM_SUSPEITO
    barrados = 0
    try:
        gateway.processar("PCDF-SIM-9999", BOLETIM_SUSPEITO, origem="delegacia-99")
    except EntradaRejeitada:
        barrados = 1

    print(gerar_relatorio_operacional(metricas, len(lote), revisados, barrados))


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
            print()
