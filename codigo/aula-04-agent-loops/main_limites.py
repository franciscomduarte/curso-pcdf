"""Nível intermediário: cada critério de parada, disparado de propósito.

    python main_limites.py
"""

from __future__ import annotations

from app.bases_sinteticas import AVISO_DADOS
from app.llm import MockReAct
from app.loop import Autonomia, LoopReAct
from app.orcamento import Orcamento

TAREFA = "Investigue o furto da motocicleta placa ABC1D23 em Taguatinga."


class NuncaEncerra:
    """LLM que só pede ferramentas — nunca dá resposta_final.
    Varia os args para não cair na trava de 'ação repetida'."""

    def pensar(self, tarefa, ferramentas, historico):
        return {"pensamento": "continuo consultando...",
                "acao": {"ferramenta": "buscar_documento",
                         "args": {"assunto": f"tema-{len(historico)}"}}}


class RepeteAcao:
    def pensar(self, tarefa, ferramentas, historico):
        return {"pensamento": "de novo a mesma coisa",
                "acao": {"ferramenta": "consultar_veiculo", "args": {"placa": "ABC1D23"}}}


def cenario(titulo: str, loop: LoopReAct, llm=None) -> None:
    if llm is not None:
        loop.llm = llm
    traco = loop.executar(TAREFA)
    print(f"\n### {titulo}")
    print(f"    parada = {traco.motivo_parada.value}")
    print(f"    {traco.orcamento.resumo()}")
    print(f"    resposta = {traco.resposta_final}")


def main() -> None:
    print(f"* {AVISO_DADOS}")

    cenario("limite de passos (max_passos=3)",
            LoopReAct(llm=NuncaEncerra(), autonomia=Autonomia.AUTONOMO,
                      orcamento=Orcamento(max_passos=3, max_chamadas=99, custo_max=999)))

    cenario("limite de chamadas (max_chamadas=2)",
            LoopReAct(llm=NuncaEncerra(), autonomia=Autonomia.AUTONOMO,
                      orcamento=Orcamento(max_passos=99, max_chamadas=2, custo_max=999)))

    cenario("limite de custo (custo_max=3, buscar_documento custa 1)",
            LoopReAct(llm=NuncaEncerra(), autonomia=Autonomia.AUTONOMO,
                      orcamento=Orcamento(max_passos=99, max_chamadas=99, custo_max=3)))

    cenario("ação repetida",
            LoopReAct(llm=RepeteAcao(), autonomia=Autonomia.AUTONOMO,
                      orcamento=Orcamento(max_passos=99, max_chamadas=99, custo_max=999)))

    cenario("ação sensível recusada pelo operador",
            LoopReAct(llm=MockReAct(), autonomia=Autonomia.LIMITADO,
                      confirmar=lambda f, a: False,
                      orcamento=Orcamento()))

    cenario("retry: servico_externo falha 2x, recupera na 3a",
            LoopReAct(llm=_UsaServicoExterno(), autonomia=Autonomia.AUTONOMO,
                      orcamento=Orcamento()))


class _UsaServicoExterno:
    def pensar(self, tarefa, ferramentas, historico):
        if not historico:
            return {"pensamento": "consulto o serviço externo",
                    "acao": {"ferramenta": "servico_externo", "args": {"recurso": "R1"}}}
        return {"pensamento": "pronto", "resposta_final": str(historico[-1]["observacao"])}


if __name__ == "__main__":
    main()
