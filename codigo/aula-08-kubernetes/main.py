"""Nível básico: sobe o cluster mínimo e roda o SIGMA nele.

    python main.py

Cada agente da Aula 7 vira um Deployment + Service. O Investigador tem 2
réplicas — rode duas ocorrências e repare que cada uma é atendida por um
pod diferente (round-robin), sem que o Fluxo saiba ou precise saber disso.
"""

from __future__ import annotations

import logging

from app.agentes import analista, consolidador, investigador, juridico
from app.bases_sinteticas import AVISO_DADOS, OCORRENCIAS
from app.cluster import Cluster
from app.fluxo import Fluxo
from app.memoria import Estado
from app.store import DecisaoHumana, Pausado, StoreCompartilhado

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def montar_cluster() -> Cluster:
    c = Cluster()
    c.criar_configmap("juridico-config", detalhe="padrao")

    c.criar_deployment("investigador-deploy", investigador, replicas=2)
    c.criar_deployment("analista-deploy", analista, replicas=1)
    c.criar_deployment("juridico-deploy", juridico, replicas=1, config_map="juridico-config")
    c.criar_deployment("consolidador-deploy", consolidador, replicas=1)

    c.criar_service("investigador-svc", "investigador-deploy")
    c.criar_service("analista-svc", "analista-deploy")
    c.criar_service("juridico-svc", "juridico-deploy")
    c.criar_service("consolidador-svc", "consolidador-deploy")
    return c


def processar(fluxo: Fluxo, oc_id: str) -> None:
    print(f"\n--- {oc_id} ---")
    r = fluxo.iniciar(Estado(id=oc_id, texto=OCORRENCIAS[oc_id]))
    assert isinstance(r, Pausado)
    print(f"  pausou: {r.pergunta}")
    print(f"  checkpoint: {r.checkpoint}")

    r = fluxo.retomar(r.checkpoint, DecisaoHumana(aprovado=True, operador="escrivão de plantão"))
    print(f"  tipificação final: {r.estado.dossie['tipificacao']}")
    print(f"  atendido por: {r.estado.atendido_por}")


def main() -> None:
    print(f"* {AVISO_DADOS}\n")

    cluster = montar_cluster()
    store = StoreCompartilhado()
    fluxo = Fluxo(cluster, store)

    print("kubectl get pods (simulado) — depois de subir os 4 Deployments:")
    print(cluster.status())

    processar(fluxo, "PCDF-SIM-0002")
    processar(fluxo, "PCDF-SIM-0009")

    print("\nkubectl get pods (simulado) — depois de 2 ocorrências:")
    print(cluster.status())
    print("\nRepare no investigador: as 2 réplicas dividiram as 2 chamadas — round-robin.")


if __name__ == "__main__":
    main()
