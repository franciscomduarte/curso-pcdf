"""HPA — herdado sem mudança da Aula 9. A mesma fórmula do HPA real do
Kubernetes (documentação oficial, "Algorithm Details"):

    desiredReplicas = ceil[replicasAtuais x (métricaAtual / métricaAlvo)]
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .cluster import Cluster


@dataclass
class HPA:
    nome: str
    deployment: str
    alvo_por_pod: float          # ex.: "queremos no máximo 3 chamadas pendentes por pod"
    min_replicas: int = 1
    max_replicas: int = 10


def avaliar(cluster: Cluster, hpa: HPA, carga_atual: float) -> dict:
    """Recebe a carga MÉDIA POR POD já calculada nesta amostra (é isso que um
    metrics-server real devolve para métricas do tipo "Pods" — a média entre
    as réplicas atuais, não o total) e escala o Deployment para perto do
    alvo, dentro de [min, max]."""
    dep = cluster.deployments[hpa.deployment]
    replicas_antes = dep.replicas

    if carga_atual <= 0:
        desejadas = hpa.min_replicas
    else:
        desejadas = math.ceil(replicas_antes * (carga_atual / hpa.alvo_por_pod))
    desejadas = max(hpa.min_replicas, min(hpa.max_replicas, desejadas))

    if desejadas != replicas_antes:
        cluster.escalar(hpa.deployment, desejadas)

    return {
        "hpa": hpa.nome, "carga_atual": carga_atual, "alvo_por_pod": hpa.alvo_por_pod,
        "replicas_antes": replicas_antes, "replicas_depois": desejadas,
    }
