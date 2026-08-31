"""Nível intermediário: um pod morre — o que acontece com o Service?

    python main_falha.py

Mostra dois cenários:
  1. Deployment com 2 réplicas: uma morre, a outra continua atendendo, e
     `reconciliar()` recria a que caiu — self-healing sem downtime.
  2. Deployment com 1 réplica: a única morre, o Service fica sem ninguém
     para atender (ServicoIndisponivel) até o próximo `reconciliar()`.
"""

from __future__ import annotations

import logging

from app.agentes import analista, investigador
from app.bases_sinteticas import AVISO_DADOS, OCORRENCIAS
from app.cluster import Cluster, ServicoIndisponivel
from app.memoria import Estado

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def cenario_1_redundancia() -> None:
    print("\n=== Cenário 1: 2 réplicas, uma morre ===")
    c = Cluster()
    c.criar_deployment("investigador-deploy", investigador, replicas=2)
    c.criar_service("investigador-svc", "investigador-deploy")

    morto = c.matar_pod("investigador-deploy", 0)
    print(f"  matei: {morto}")
    print(f"  status:\n{_indenta(c.status())}")

    e = Estado(id="PCDF-SIM-0002", texto=OCORRENCIAS["PCDF-SIM-0002"])
    _, pod = c.chamar("investigador-svc", e)
    print(f"  a chamada AINDA funcionou — atendida por {pod} (a réplica sobrevivente)")

    recriados = c.reconciliar()
    print(f"  reconciliar() recriou: {recriados}")
    print(f"  status depois de reconciliar:\n{_indenta(c.status())}")


def cenario_2_sem_redundancia() -> None:
    print("\n=== Cenário 2: 1 réplica, a única morre ===")
    c = Cluster()
    c.criar_deployment("analista-deploy", analista, replicas=1)
    c.criar_service("analista-svc", "analista-deploy")

    morto = c.matar_pod("analista-deploy", 0)
    print(f"  matei: {morto}")

    e = Estado(id="PCDF-SIM-0002", texto=OCORRENCIAS["PCDF-SIM-0002"])
    try:
        c.chamar("analista-svc", e)
        print("  (não deveria chegar aqui)")
    except ServicoIndisponivel as exc:
        print(f"  a chamada FALHOU: {exc}")

    c.reconciliar()
    _, pod = c.chamar("analista-svc", e)
    print(f"  depois de reconciliar(), a chamada funciona de novo — atendida por {pod}")


def _indenta(texto: str) -> str:
    return "\n".join(f"    {linha}" for linha in texto.splitlines())


def main() -> None:
    print(f"* {AVISO_DADOS}")
    cenario_1_redundancia()
    cenario_2_sem_redundancia()


if __name__ == "__main__":
    main()
