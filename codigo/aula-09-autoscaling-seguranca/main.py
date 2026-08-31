"""Nível básico: o cluster da Aula 8 + autoscaler + guardrail + métricas.

    python main.py

Mostra, nesta ordem: (1) dois boletins processados normalmente pelo Gateway;
(2) um boletim com injeção sendo barrado pelo guardrail; (3) uma origem
estourando o limite de taxa; (4) o HPA do investigador reagindo a uma carga
simulada (sobe, depois desce); (5) o painel de métricas final.
"""

from __future__ import annotations

import logging

from app.agentes import analista, consolidador, investigador, juridico
from app.autoscaler import HPA, avaliar
from app.bases_sinteticas import AVISO_DADOS, BOLETIM_SUSPEITO, OCORRENCIAS
from app.cluster import Cluster
from app.fluxo import Fluxo
from app.gateway import Gateway
from app.guardrail import EntradaRejeitada, Guardrail, TaxaExcedida
from app.observabilidade import Metricas
from app.store import DecisaoHumana, Pausado, StoreCompartilhado

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def montar_cluster(metricas: Metricas) -> Cluster:
    c = Cluster(metricas=metricas)
    c.criar_configmap("juridico-config", detalhe="padrao")
    c.criar_deployment("investigador-deploy", investigador, replicas=1)
    c.criar_deployment("analista-deploy", analista, replicas=1)
    c.criar_deployment("juridico-deploy", juridico, replicas=1, config_map="juridico-config")
    c.criar_deployment("consolidador-deploy", consolidador, replicas=1)
    c.criar_service("investigador-svc", "investigador-deploy")
    c.criar_service("analista-svc", "analista-deploy")
    c.criar_service("juridico-svc", "juridico-deploy")
    c.criar_service("consolidador-svc", "consolidador-deploy")
    return c


def processar_e_aprovar(gateway: Gateway, oc_id: str, texto: str, origem: str) -> None:
    r = gateway.processar(oc_id, texto, origem=origem)
    assert isinstance(r, Pausado)
    r2 = gateway.fluxo.retomar(r.checkpoint, DecisaoHumana(aprovado=True, operador="escrivão de plantão"))
    print(f"  {oc_id}: {r2.estado.dossie['tipificacao']['artigo']}")


def main() -> None:
    print(f"* {AVISO_DADOS}\n")

    metricas = Metricas()
    cluster = montar_cluster(metricas)
    store = StoreCompartilhado()
    gateway = Gateway(Fluxo(cluster, store), Guardrail(limite_por_janela=3, janela_s=60.0))

    print("=== 1. Dois boletins normais, pelo Gateway ===")
    processar_e_aprovar(gateway, "PCDF-SIM-0002", OCORRENCIAS["PCDF-SIM-0002"], origem="delegacia-01")
    processar_e_aprovar(gateway, "PCDF-SIM-0009", OCORRENCIAS["PCDF-SIM-0009"], origem="delegacia-01")

    print("\n=== 2. Um boletim com injeção — o guardrail barra antes do fluxo ===")
    try:
        gateway.processar("PCDF-SIM-9999", BOLETIM_SUSPEITO, origem="delegacia-02")
        print("  (não deveria chegar aqui)")
    except EntradaRejeitada as exc:
        print(f"  REJEITADO: {exc}")

    print("\n=== 3. Uma origem estourando o limite de taxa (3 chamadas / 60s) ===")
    for i in range(4):
        try:
            gateway.processar("PCDF-SIM-0015", OCORRENCIAS["PCDF-SIM-0015"], origem="delegacia-03")
            print(f"  chamada {i + 1}: permitida")
        except TaxaExcedida as exc:
            print(f"  chamada {i + 1}: BARRADA — {exc}")

    print("\n=== 4. HPA do investigador reagindo à carga ===")
    hpa = HPA(nome="investigador-hpa", deployment="investigador-deploy",
              alvo_por_pod=3.0, min_replicas=1, max_replicas=4)
    for rotulo, carga in (("normal", 2.0), ("pico", 9.0), ("pico sustentado", 11.0), ("ocioso", 0.0)):
        resultado = avaliar(cluster, hpa, carga)
        print(f"  carga {rotulo:<16} ({carga:>4.1f}) -> "
              f"{resultado['replicas_antes']} -> {resultado['replicas_depois']} réplicas")

    print("\n=== 5. Painel de métricas ===")
    print(metricas.painel())


if __name__ == "__main__":
    main()
