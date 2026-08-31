"""Gabarito dos laboratórios da Aula 4.

    python solucao_exercicios.py            # todos
    python solucao_exercicios.py basico     # um lab por vez
    python solucao_exercicios.py intermediario
    python solucao_exercicios.py sem-progresso
    python solucao_exercicios.py desafio
"""

from __future__ import annotations

import sys

from app.barramento import Auditor, Barramento
from app.ferramentas import REGISTRO, Ferramenta
from app.llm import MockReAct
from app.loop import Autonomia, LoopReAct, PassoTraco, TracoExecucao
from app.orcamento import MotivoParada, Orcamento

TAREFA = "Furto da moto placa ABC1D23 em Taguatinga."


# ---------------------------------------------------------------------------
# LAB BÁSICO — nível de autonomia muda quando o loop pausa
# ---------------------------------------------------------------------------
def lab_basico() -> None:
    print("== LAB BÁSICO: autonomia ==")
    for nivel in Autonomia:
        pausas: list[str] = []
        LoopReAct(llm=MockReAct(), autonomia=nivel,
                  confirmar=lambda f, a, p=pausas: (p.append(f) or True),
                  orcamento=Orcamento()).executar(TAREFA)
        print(f"  {nivel.value:<16} pediu confirmação para: {pausas or '(nada)'}")


# ---------------------------------------------------------------------------
# LAB BÁSICO (parte 2) — novo critério de parada SEM_PROGRESSO
# ---------------------------------------------------------------------------
_VAZIAS = ("[]", "{}", "não encontrado")


class SoConsultaVazio:
    """Sempre chama consultar_ocorrencias_similares numa região sem histórico."""

    def pensar(self, tarefa, ferramentas, historico):
        return {"pensamento": "vou tentar de novo...",
                "acao": {"ferramenta": "consultar_ocorrencias_similares",
                         "args": {"regiao": f"Lugar-{len(historico)}"}}}


class LoopComSemProgresso(LoopReAct):
    """LoopReAct + um oitavo critério: as últimas 3 observações vieram vazias.

    Reimplementa o laço (não dá para só "encaixar" a checagem por fora — o
    critério precisa ser visto DEPOIS de cada observação, ainda dentro do
    loop, para poder parar antes do próximo passo custar orçamento). Fora
    isso, o corpo é o mesmo `LoopReAct.executar()` da Aula 4.
    """

    def executar(self, tarefa: str) -> TracoExecucao:
        traco = TracoExecucao(tarefa=tarefa, orcamento=self.orcamento)
        self.orcamento.iniciar()
        historico: list[dict] = []

        while True:
            parada = self.orcamento.excedido()
            if parada:
                traco.motivo_parada = parada
                traco.resposta_final = f"Interrompido: {parada.value}. Entregar o parcial."
                return traco

            self.orcamento.passos += 1
            decisao = self.llm.pensar(tarefa, list(self.ferramentas.values()), historico)
            pensamento = decisao.get("pensamento", "")

            if "resposta_final" in decisao:
                traco.passos.append(PassoTraco(self.orcamento.passos, pensamento))
                traco.resposta_final = decisao["resposta_final"]
                traco.motivo_parada = MotivoParada.RESPOSTA_FINAL
                return traco

            acao = decisao["acao"]
            nome, args = acao["ferramenta"], acao.get("args", {})
            ferramenta = self.ferramentas[nome]
            observacao, tentativas = self._executar_com_retry(ferramenta, args)
            self.orcamento.chamadas += 1
            self.orcamento.custo += ferramenta.custo
            historico.append({**decisao, "observacao": observacao})
            traco.passos.append(PassoTraco(self.orcamento.passos, pensamento, nome, args,
                                           str(observacao), tentativas))

            ultimas = traco.passos[-3:]                          # critério 8: SEM_PROGRESSO
            if len(ultimas) == 3 and all(p.observacao in _VAZIAS for p in ultimas):
                traco.motivo_parada = MotivoParada.SEM_PROGRESSO
                traco.resposta_final = "Sem progresso nas últimas 3 consultas — entregar parcial."
                return traco


def lab_sem_progresso() -> None:
    print("\n== LAB BÁSICO (2): critério SEM_PROGRESSO ==")
    loop = LoopComSemProgresso(llm=SoConsultaVazio(), autonomia=Autonomia.AUTONOMO,
                               orcamento=Orcamento(max_passos=5))
    traco = loop.executar("investigação sem pistas")
    print(f"  parada = {traco.motivo_parada.value}")
    print(f"  resposta = {traco.resposta_final}")


# ---------------------------------------------------------------------------
# LAB INTERMEDIÁRIO — orçamento por tarefa + evento de encerramento no barramento
# ---------------------------------------------------------------------------
def orcamento_para(tarefa: str) -> Orcamento:
    t = tarefa.lower()
    if "triagem" in t or "rápid" in t or "rapid" in t:
        return Orcamento(max_passos=3, max_chamadas=4, custo_max=8)
    return Orcamento(max_passos=8, max_chamadas=12, custo_max=30)


def executar_e_publicar(tarefa: str, barramento: Barramento):
    orc = orcamento_para(tarefa)
    traco = LoopReAct(llm=MockReAct(), autonomia=Autonomia.AUTONOMO, orcamento=orc).executar(tarefa)
    barramento.publicar("agente.encerrou", "agente-consultor", {
        "motivo_parada": traco.motivo_parada.value,
        "passos": orc.passos, "custo": orc.custo,
        "tem_parcial": traco.motivo_parada is not MotivoParada.RESPOSTA_FINAL,
    })
    return traco


def lab_intermediario() -> None:
    print("\n== LAB INTERMEDIÁRIO: orçamento por tarefa + evento ao Auditor ==")
    bus, auditor = Barramento(), Auditor()
    bus.assinar("#", auditor.ao_receber)

    executar_e_publicar("triagem rápida do furto da moto ABC1D23 em Taguatinga", bus)
    executar_e_publicar("investigação do furto da moto ABC1D23 em Taguatinga", bus)

    print(f"  o Auditor recebeu {len(auditor.trilha)} eventos de encerramento:")
    for ev in auditor.trilha:
        print(f"    {ev.dados}")
    assert len(auditor.trilha) == 2


# ---------------------------------------------------------------------------
# DESAFIO — ferramenta com timeout próprio
# ---------------------------------------------------------------------------
def desafio() -> None:
    print("\n== DESAFIO: ferramenta lenta + tempo_max_s ==")
    import time

    REGISTRO["consulta_lenta"] = Ferramenta(
        "consulta_lenta", "demora de propósito",
        lambda alvo: time.sleep(0.3) or {"alvo": alvo, "ok": True}, custo=1)

    class UsaLenta:
        def pensar(self, tarefa, ferramentas, historico):
            return {"pensamento": "consulto a lenta",
                    "acao": {"ferramenta": "consulta_lenta", "args": {"alvo": f"a{len(historico)}"}}}

    try:
        traco = LoopReAct(llm=UsaLenta(), autonomia=Autonomia.AUTONOMO,
                          orcamento=Orcamento(tempo_max_s=0.5, max_passos=99,
                                              max_chamadas=99)).executar("qualquer")
        print(f"  parada = {traco.motivo_parada.value} após ~{len(traco.passos)} passos")
    finally:
        del REGISTRO["consulta_lenta"]


LABS = {
    "basico": lab_basico,
    "sem-progresso": lab_sem_progresso,
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
