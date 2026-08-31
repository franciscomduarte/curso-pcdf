"""Nível intermediário: diagnostique um incidente usando só métricas e traço.

    python main_incidente.py

Simula um problema real (o `juridico-deploy` fica sem nenhum pod Running por
um tempo, sem ninguém rodar `reconciliar()`) e processa boletins durante
esse período. O objetivo do exercício NÃO é ler este arquivo — é olhar
`metricas.painel()` e o traço de uma investigação que falhou, e responder:
qual serviço está com problema, e o que aconteceu.
"""

from __future__ import annotations

import logging

from app.agentes import analista, consolidador, investigador, juridico
from app.bases_sinteticas import AVISO_DADOS, OCORRENCIAS
from app.cluster import Cluster, ServicoIndisponivel
from app.fluxo import Fluxo
from app.observabilidade import Metricas, formatar_traco
from app.store import Pausado, StoreCompartilhado

logging.basicConfig(level=logging.WARNING)   # silencia o INFO de roteamento — só o essencial


def montar_cluster(metricas: Metricas) -> Cluster:
    c = Cluster(metricas=metricas)
    c.criar_deployment("investigador-deploy", investigador, replicas=1)
    c.criar_deployment("analista-deploy", analista, replicas=1)
    c.criar_deployment("juridico-deploy", juridico, replicas=1)
    c.criar_deployment("consolidador-deploy", consolidador, replicas=1)
    c.criar_service("investigador-svc", "investigador-deploy")
    c.criar_service("analista-svc", "analista-deploy")
    c.criar_service("juridico-svc", "juridico-deploy")
    c.criar_service("consolidador-svc", "consolidador-deploy")
    return c


def main() -> None:
    print(f"* {AVISO_DADOS}\n")
    metricas = Metricas()
    cluster = montar_cluster(metricas)
    fluxo = Fluxo(cluster, StoreCompartilhado())

    print("--- processando PCDF-SIM-0002 (tudo saudável) ---")
    r1 = fluxo.iniciar(_estado("PCDF-SIM-0002"))
    assert isinstance(r1, Pausado)
    print("  pausou normalmente no breakpoint.\n")

    cluster.matar_pod("juridico-deploy", 0)   # incidente: única réplica do Jurídico cai

    print("--- processando mais 3 boletins durante o incidente ---")
    for oc_id in ("PCDF-SIM-0009", "PCDF-SIM-0015", "PCDF-SIM-0002"):
        try:
            fluxo.iniciar(_estado(oc_id))
            print(f"  {oc_id}: OK")
        except ServicoIndisponivel as exc:
            print(f"  {oc_id}: FALHOU — {exc}")

    print("\n=== painel de métricas (o que você tem para diagnosticar) ===")
    print(metricas.painel())

    print("\n=== traço da PRIMEIRA investigação (antes do incidente) ===")
    e1 = fluxo.store.carregar(r1.checkpoint)
    print(formatar_traco(e1.atendido_por))


def _estado(oc_id: str):
    from app.memoria import Estado
    return Estado(id=oc_id, texto=OCORRENCIAS[oc_id])


if __name__ == "__main__":
    main()
