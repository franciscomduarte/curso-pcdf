"""O motor de cluster — herdado sem nenhuma mudança das Aulas 8-9.

Esta é a peça que mais se repete no curso, de propósito: um Deployment com
N réplicas, um Service que roteia por round-robin, `reconciliar()` como
self-healing, e `chamar()` cronometrando cada chamada para `Metricas`. O que
muda nesta aula é o que roda EM CIMA dele (ver `fluxo.py`/`roteador.py`) —
não o cluster em si.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from itertools import count
from typing import Callable

from .observabilidade import Metricas

logger = logging.getLogger("sigma.cluster")

Imagem = Callable[..., object]   # (estado, config: dict) -> estado


class ServicoIndisponivel(Exception):
    """Nenhum Pod Running atrás do Service — equivalente a um 503."""


@dataclass
class ConfigMap:
    nome: str
    dados: dict[str, str] = field(default_factory=dict)


@dataclass
class Pod:
    nome: str
    deployment: str
    status: str = "Running"        # Running | CrashLoopBackOff
    chamadas_atendidas: int = 0


@dataclass
class Deployment:
    nome: str
    imagem: Imagem
    replicas: int = 1
    config_map: str | None = None
    pods: list[Pod] = field(default_factory=list)


@dataclass
class Service:
    nome: str
    deployment: str   # seletor — nesta versão mínima, 1 Service : 1 Deployment


class Cluster:
    """O "control plane" mínimo: cria recursos, roteia chamadas, reconcilia, mede."""

    def __init__(self, metricas: Metricas | None = None) -> None:
        self.configmaps: dict[str, ConfigMap] = {}
        self.deployments: dict[str, Deployment] = {}
        self.services: dict[str, Service] = {}
        self.eventos: list[str] = []
        self.metricas = metricas if metricas is not None else Metricas()
        self._contador = count(1)
        self._proximo: dict[str, int] = {}      # round-robin por deployment

    # -- recursos ---------------------------------------------------------
    def criar_configmap(self, nome: str, **dados: str) -> ConfigMap:
        cm = ConfigMap(nome, dados)
        self.configmaps[nome] = cm
        self._log(f"configmap/{nome} criado {dados}")
        return cm

    def criar_deployment(self, nome: str, imagem: Imagem, replicas: int = 1,
                          config_map: str | None = None) -> Deployment:
        dep = Deployment(nome, imagem, replicas=replicas, config_map=config_map)
        self.deployments[nome] = dep
        self._proximo[nome] = 0
        self._escalar_pods(dep)
        self._log(f"deployment/{nome} criado replicas={replicas}")
        return dep

    def criar_service(self, nome: str, deployment: str) -> Service:
        if deployment not in self.deployments:
            raise KeyError(f"deployment '{deployment}' não existe")
        svc = Service(nome, deployment)
        self.services[nome] = svc
        self._log(f"service/{nome} -> deployment/{deployment}")
        return svc

    # -- operação -----------------------------------------------------
    def escalar(self, deployment: str, replicas: int) -> None:
        dep = self.deployments[deployment]
        dep.replicas = replicas
        self._escalar_pods(dep)
        self._log(f"deployment/{deployment} escalado para replicas={replicas}")

    def matar_pod(self, deployment: str, indice: int = 0) -> str:
        dep = self.deployments[deployment]
        vivos = [p for p in dep.pods if p.status == "Running"]
        if indice >= len(vivos):
            raise IndexError(f"deployment/{deployment} não tem pod Running no índice {indice}")
        pod = vivos[indice]
        pod.status = "CrashLoopBackOff"
        self._log(f"pod/{pod.nome} morreu (CrashLoopBackOff)")
        return pod.nome

    def reconciliar(self) -> list[str]:
        """O 'controller loop': para cada Deployment, garante N pods Running."""
        recriados = []
        for dep in self.deployments.values():
            dep.pods = [p for p in dep.pods if p.status == "Running"]
            faltam = dep.replicas - len(dep.pods)
            for _ in range(max(0, faltam)):
                novo = self._novo_pod(dep)
                dep.pods.append(novo)
                recriados.append(novo.nome)
                self._log(f"pod/{novo.nome} recriado (self-healing)")
        return recriados

    def chamar(self, servico: str, *args, **kwargs):
        """Resolve o Service -> escolhe um Pod Running (round-robin) -> chama a
        imagem, cronometrando e registrando em `self.metricas`."""
        svc = self.services[servico]
        dep = self.deployments[svc.deployment]
        vivos = [p for p in dep.pods if p.status == "Running"]
        if not vivos:
            self._log(f"service/{servico}: SEM pods Running — chamada falhou")
            self.metricas.registrar(servico, 0.0, ok=False)
            raise ServicoIndisponivel(
                f"service/{servico} não tem nenhum pod Running em deployment/{dep.nome}")

        i = self._proximo[dep.nome] % len(vivos)
        self._proximo[dep.nome] += 1
        pod = vivos[i]
        pod.chamadas_atendidas += 1

        config = dict(self.configmaps[dep.config_map].dados) if dep.config_map else {}
        self._log(f"service/{servico} roteou para {pod.nome}")

        inicio = time.perf_counter()
        resultado = dep.imagem(*args, config=config, **kwargs)
        duracao_ms = (time.perf_counter() - inicio) * 1000
        self.metricas.registrar(servico, duracao_ms, ok=True)
        return resultado, pod.nome, duracao_ms

    def status(self) -> str:
        linhas = [f"{'NAME':<28} {'STATUS':<20} CHAMADAS"]
        for dep in self.deployments.values():
            for p in dep.pods:
                linhas.append(f"{p.nome:<28} {p.status:<20} {p.chamadas_atendidas}")
        return "\n".join(linhas)

    # -- interno ------------------------------------------------------
    def _escalar_pods(self, dep: Deployment) -> None:
        vivos = [p for p in dep.pods if p.status == "Running"]
        dep.pods = vivos
        while len(dep.pods) < dep.replicas:
            dep.pods.append(self._novo_pod(dep))
        if len(dep.pods) > dep.replicas:
            dep.pods = dep.pods[: dep.replicas]

    def _novo_pod(self, dep: Deployment) -> Pod:
        n = next(self._contador)
        return Pod(nome=f"{dep.nome}-{n:04x}", deployment=dep.nome)

    def _log(self, msg: str) -> None:
        self.eventos.append(msg)
        logger.info(msg)
