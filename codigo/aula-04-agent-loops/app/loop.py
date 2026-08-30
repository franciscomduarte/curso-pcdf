"""LoopReAct — o ciclo Percepção → Planejamento → Decisão → Ação → Observação.

Uma volta do loop:

  PERCEPÇÃO   : o loop reúne o que já sabe (tarefa + histórico)
  PLANEJAMENTO: o LLM produz um "pensamento"
  DECISÃO     : o LLM escolhe uma ação (ferramenta) ou encerra
  AÇÃO        : o loop executa a ferramenta (com retry) — se a política de
                autonomia exigir, pede confirmação humana antes
  OBSERVAÇÃO  : o resultado (ou erro) entra no histórico

Depois de cada volta o loop checa TODOS os critérios de parada (orcamento.py).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum

from .ferramentas import REGISTRO, Ferramenta
from .orcamento import MotivoParada, Orcamento

logger = logging.getLogger("sigma.loop")


class Autonomia(str, Enum):
    SUPERVISIONADO = "supervisionado"   # confirma TODA ação
    LIMITADO = "limitado"               # confirma só ações sensíveis
    AUTONOMO = "autonomo"               # não confirma nada


@dataclass
class PassoTraco:
    n: int
    pensamento: str
    ferramenta: str | None = None
    args: dict = field(default_factory=dict)
    observacao: str = ""
    tentativas: int = 1


@dataclass
class TracoExecucao:
    tarefa: str
    passos: list[PassoTraco] = field(default_factory=list)
    resposta_final: str = ""
    motivo_parada: MotivoParada = MotivoParada.RESPOSTA_FINAL
    orcamento: Orcamento | None = None

    def texto_react(self, limite: int = 160) -> str:
        def corta(s: str) -> str:
            s = str(s).replace("\n", " ")
            return s if len(s) <= limite else s[: limite - 1] + "…"

        linhas = [f"Tarefa: {self.tarefa}", ""]
        for p in self.passos:
            linhas.append(f"Pensamento {p.n}: {p.pensamento}")
            if p.ferramenta:
                sufixo = f"  (após {p.tentativas} tentativas)" if p.tentativas > 1 else ""
                linhas.append(f"Ação {p.n}: {p.ferramenta}[{corta(p.args)}]{sufixo}")
                linhas.append(f"Observação {p.n}: {corta(p.observacao)}")
            linhas.append("")
        linhas.append(f"Resposta final: {corta(self.resposta_final)}")
        linhas.append(f"(parada: {self.motivo_parada.value} — {self.orcamento.resumo()})")
        return "\n".join(linhas)


# confirmação: recebe (ferramenta, args) -> bool
def _sempre_sim(_f: str, _a: dict) -> bool:
    return True


@dataclass
class LoopReAct:
    llm: object
    orcamento: Orcamento = field(default_factory=Orcamento)
    autonomia: Autonomia = Autonomia.LIMITADO
    confirmar: object = _sempre_sim
    ferramentas: dict[str, Ferramenta] = field(default_factory=lambda: dict(REGISTRO))
    retries: int = 3
    espera_base: float = 0.0   # 0 nos testes; use ~1.5 em produção

    def executar(self, tarefa: str) -> TracoExecucao:
        traco = TracoExecucao(tarefa=tarefa, orcamento=self.orcamento)
        self.orcamento.iniciar()
        historico: list[dict] = []
        ultima_acao: tuple | None = None

        while True:
            parada = self.orcamento.excedido()
            if parada:
                traco.motivo_parada = parada
                traco.resposta_final = f"Interrompido: {parada.value}. Entregar o parcial."
                return traco

            self.orcamento.passos += 1
            specs = list(self.ferramentas.values())
            decisao = self.llm.pensar(tarefa, specs, historico)          # PLANEJAMENTO
            pensamento = decisao.get("pensamento", "")

            if "resposta_final" in decisao:                              # DECISÃO: encerrar
                traco.passos.append(PassoTraco(self.orcamento.passos, pensamento))
                traco.resposta_final = decisao["resposta_final"]
                traco.motivo_parada = MotivoParada.RESPOSTA_FINAL
                return traco

            acao = decisao["acao"]                                      # DECISÃO: agir
            nome, args = acao["ferramenta"], acao.get("args", {})
            assinatura = (nome, tuple(sorted(args.items())))
            if assinatura == ultima_acao:
                traco.passos.append(PassoTraco(self.orcamento.passos, pensamento, nome, args,
                                               "abortado: ação idêntica à anterior"))
                traco.motivo_parada = MotivoParada.ACAO_REPETIDA
                traco.resposta_final = "Loop detectado — mesma ação repetida. Entregar o parcial."
                return traco
            ultima_acao = assinatura

            ferramenta = self.ferramentas.get(nome)
            if ferramenta is None:
                obs = f"ferramenta desconhecida: {nome}"
                historico.append({**decisao, "observacao": obs})
                traco.passos.append(PassoTraco(self.orcamento.passos, pensamento, nome, args, obs))
                continue

            if self._precisa_confirmar(ferramenta) and not self.confirmar(nome, args):
                traco.passos.append(PassoTraco(self.orcamento.passos, pensamento, nome, args,
                                               "não confirmado pelo operador"))
                traco.motivo_parada = MotivoParada.NAO_CONFIRMADO
                traco.resposta_final = "Ação sensível não autorizada — encerrando."
                return traco

            observacao, tentativas = self._executar_com_retry(ferramenta, args)  # AÇÃO
            self.orcamento.chamadas += 1
            self.orcamento.custo += ferramenta.custo
            historico.append({**decisao, "observacao": observacao})             # OBSERVAÇÃO
            traco.passos.append(PassoTraco(self.orcamento.passos, pensamento, nome, args,
                                           str(observacao), tentativas))

    # -- helpers ---------------------------------------------------------
    def _precisa_confirmar(self, f: Ferramenta) -> bool:
        if self.autonomia is Autonomia.AUTONOMO:
            return False
        if self.autonomia is Autonomia.SUPERVISIONADO:
            return True
        return f.sensivel   # LIMITADO

    def _executar_com_retry(self, f: Ferramenta, args: dict):
        erro = None
        for tentativa in range(1, self.retries + 1):
            try:
                return f.funcao(**args), tentativa
            except TypeError as exc:            # args errados: não adianta repetir
                return f"argumentos inválidos: {exc}", tentativa
            except Exception as exc:            # transitório: tenta de novo
                erro = exc
                logger.warning("%s falhou (tentativa %d): %s", f.nome, tentativa, exc)
                if tentativa < self.retries:
                    time.sleep(self.espera_base * 2 ** (tentativa - 1))
        return f"falhou após {self.retries} tentativas: {erro}", self.retries
