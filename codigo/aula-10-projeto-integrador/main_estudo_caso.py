"""Nível intermediário: a Operação Vetor — o estudo de caso da aula, com o
SIGMA completo processando um lote misto, sob o mesmo guardrail e o mesmo
HPA da Aula 9.

    python main_estudo_caso.py

Cenário (fictício, ver Bloco 1 da aula): quatro boletins de origens
diferentes chegam numa janela curta, mais um boletim malicioso tentando se
passar por uma quinta origem. O objetivo do script é mostrar o SIGMA
segurando essa carga mista: roteamento diferenciado por gravidade, guardrail
na entrada, HPA reagindo ao volume — e terminar com o mesmo tipo de painel
que um operador real consultaria.
"""

from __future__ import annotations

import logging

from app.agentes import analista, consolidador, investigador, juridico, revisor_dupla
from app.autoscaler import HPA, avaliar
from app.bases_sinteticas import AVISO_DADOS, BOLETIM_SUSPEITO, OCORRENCIAS
from app.cluster import Cluster
from app.fluxo import Fluxo
from app.gateway import Gateway
from app.guardrail import EntradaRejeitada, Guardrail
from app.observabilidade import Metricas
from app.store import DecisaoHumana, Pausado, StoreCompartilhado

logging.basicConfig(level=logging.WARNING)   # só o essencial — como um operador real veria

LOTE = [
    ("PCDF-SIM-0002", "delegacia-01"),
    ("PCDF-SIM-0009", "delegacia-02"),
    ("PCDF-SIM-0015", "delegacia-03"),
    ("PCDF-SIM-0021", "delegacia-04"),
]


def montar_cluster(metricas: Metricas) -> Cluster:
    c = Cluster(metricas=metricas)
    c.criar_configmap("juridico-config", detalhe="padrao")
    c.criar_deployment("investigador-deploy", investigador, replicas=1)
    c.criar_deployment("analista-deploy", analista, replicas=1)
    c.criar_deployment("juridico-deploy", juridico, replicas=1, config_map="juridico-config")
    c.criar_deployment("revisor-deploy", revisor_dupla, replicas=1)
    c.criar_deployment("consolidador-deploy", consolidador, replicas=1)
    for base in ("investigador", "analista", "juridico", "revisor", "consolidador"):
        c.criar_service(f"{base}-svc", f"{base}-deploy")
    return c


def main() -> None:
    print(f"* {AVISO_DADOS}\n")
    metricas = Metricas()
    cluster = montar_cluster(metricas)
    gateway = Gateway(Fluxo(cluster, StoreCompartilhado()), Guardrail(limite_por_janela=10))

    print(f"=== Operação Vetor: lote de {len(LOTE)} boletins + 1 tentativa de injeção ===")
    revisados, diretos = 0, 0
    for oc_id, origem in LOTE:
        r = gateway.processar(oc_id, OCORRENCIAS[oc_id], origem=origem)
        assert isinstance(r, Pausado)
        r2 = gateway.fluxo.retomar(r.checkpoint, DecisaoHumana(aprovado=True, operador="mutirão"))
        rota = " -> ".join(p["etapa"] for p in r2.estado.atendido_por)
        if "revisar" in rota:
            revisados += 1
        else:
            diretos += 1
        print(f"  {oc_id} ({origem}): {r2.estado.dossie['tipificacao']['artigo']} [{rota}]")

    print("\n=== Uma origem tenta se passar por delegacia legítima, com injeção ===")
    try:
        gateway.processar("PCDF-SIM-9999", BOLETIM_SUSPEITO, origem="delegacia-05")
        print("  (não deveria chegar aqui)")
    except EntradaRejeitada as exc:
        print(f"  BARRADO na entrada: {exc}")

    print("\n=== HPA reage ao volume do lote (4 boletins numa janela curta) ===")
    hpa = HPA(nome="investigador-hpa", deployment="investigador-deploy",
              alvo_por_pod=2.0, min_replicas=1, max_replicas=4)
    resultado = avaliar(cluster, hpa, carga_atual=float(len(LOTE)))
    print(f"  carga={resultado['carga_atual']:.1f} -> "
          f"{resultado['replicas_antes']} -> {resultado['replicas_depois']} réplicas")

    print(f"\n=== Resumo da operação ===")
    print(f"  processados: {len(LOTE)} · com revisão dupla: {revisados} · diretos: {diretos} "
          f"· barrados na entrada: 1")
    print("\n=== Painel de métricas ===")
    print(metricas.painel())


if __name__ == "__main__":
    main()
