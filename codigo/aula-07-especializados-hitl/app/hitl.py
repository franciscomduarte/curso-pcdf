"""Human-in-the-loop: o fluxo PARA numa ação sensível e espera um humano.

Peças:
  - PausaParaHumano : o "breakpoint" — o fluxo interrompe e devolve o controle
  - Checkpoint      : salva/carrega o Estado (JSON) — é o que permite retomar
                      depois, até de outro processo
  - Fluxo           : investigar -> analisar -> jurídico -> [BREAKPOINT] -> consolidar
      · iniciar(estado)               -> Pausado | Concluido
      · retomar(checkpoint, decisao)  -> Pausado | Concluido

O breakpoint fica ANTES de a tipificação virar definitiva: o sistema propõe,
o servidor decide. Rejeitar sem correção manda de volta ao Jurídico (ciclo HITL).
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from . import agentes
from .memoria import Estado

SAIDA = Path(__file__).resolve().parent.parent / "saida"


class PausaParaHumano(Exception):
    def __init__(self, checkpoint: str, proposta: dict, pergunta: str) -> None:
        super().__init__(pergunta)
        self.checkpoint = checkpoint
        self.proposta = proposta
        self.pergunta = pergunta


# --- checkpoint -------------------------------------------------------
class Checkpoint:
    @staticmethod
    def salvar(estado: Estado) -> str:
        SAIDA.mkdir(exist_ok=True)
        cid = f"{estado.id}--{uuid.uuid4().hex[:8]}"
        (SAIDA / f"{cid}.json").write_text(
            json.dumps(estado.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return cid

    @staticmethod
    def carregar(cid: str) -> Estado:
        dados = json.loads((SAIDA / f"{cid}.json").read_text(encoding="utf-8"))
        return Estado.from_dict(dados)


# --- decisão e resultado -------------------------------------------
@dataclass
class DecisaoHumana:
    aprovado: bool
    tipificacao_corrigida: dict | None = None
    nota: str = ""
    operador: str = "servidor"


@dataclass
class Pausado:
    checkpoint: str
    proposta: dict
    pergunta: str


@dataclass
class Concluido:
    estado: Estado


# --- o fluxo -------------------------------------------------------
ORDEM = {"investigar": agentes.investigador,
         "analisar": agentes.analista,
         "juridico": agentes.juridico,
         "consolidar": agentes.consolidador}
PROXIMA = {"investigar": "analisar", "analisar": "juridico",
           "juridico": "aguardando_aprovacao", "consolidar": "fim"}


class Fluxo:
    def __init__(self, max_ciclos_hitl: int = 3) -> None:
        self.max_ciclos_hitl = max_ciclos_hitl

    def _rodar(self, e: Estado):
        while e.etapa not in ("fim", "aguardando_aprovacao"):
            e = ORDEM[e.etapa](e)
            e.etapa = PROXIMA[e.etapa]
        if e.etapa == "aguardando_aprovacao":
            cid = Checkpoint.salvar(e)
            raise PausaParaHumano(
                cid, e.tipificacao_proposta,
                f"Aprovar a tipificação proposta para {e.id}? "
                "(aprovar / corrigir / rejeitar-com-nota)",
            )
        return Concluido(e)

    def iniciar(self, estado: Estado):
        try:
            return self._rodar(estado)
        except PausaParaHumano as p:
            return Pausado(p.checkpoint, p.proposta, p.pergunta)

    def retomar(self, checkpoint: str, decisao: DecisaoHumana):
        e = Checkpoint.carregar(checkpoint)
        e.aprovacoes.append({
            "quando": datetime.now(timezone.utc).isoformat(),
            "operador": decisao.operador,
            "aprovado": decisao.aprovado,
            "nota": decisao.nota,
            "corrigiu": decisao.tipificacao_corrigida is not None,
        })

        if decisao.aprovado:
            e.tipificacao_final = e.tipificacao_proposta
            e.etapa = "consolidar"
        elif decisao.tipificacao_corrigida:
            e.tipificacao_final = {**decisao.tipificacao_corrigida, "origem": "correção humana"}
            e.etapa = "consolidar"
        else:
            # rejeitado sem correção -> volta ao Jurídico com a nota (ciclo HITL)
            rejeicoes = sum(1 for a in e.aprovacoes if not a["aprovado"] and not a["corrigiu"])
            if rejeicoes >= self.max_ciclos_hitl:
                e.tipificacao_final = {"artigo": "PENDENTE", "natureza": "indefinida",
                                       "origem": f"{rejeicoes} rejeições — encaminhado ao humano"}
                e.etapa = "consolidar"
            else:
                e.etapa = "juridico"

        try:
            return self._rodar(e)
        except PausaParaHumano as p:
            return Pausado(p.checkpoint, p.proposta, p.pergunta)
