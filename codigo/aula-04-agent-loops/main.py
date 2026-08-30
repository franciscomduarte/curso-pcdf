"""Nível básico: o loop ReAct monta uma linha do tempo, reagindo às observações.

    python main.py

Compare com a Aula 3: lá o plano era fixo. Aqui o agente só busca o auto de
apreensão PORQUE o veículo constava alerta — é uma decisão tomada no passo,
com base na observação anterior.
"""

from __future__ import annotations

import logging

from dotenv import load_dotenv

from app.bases_sinteticas import AVISO_DADOS
from app.llm import llm_padrao
from app.loop import Autonomia, LoopReAct
from app.orcamento import Orcamento

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

TAREFA = (
    "Monte uma linha do tempo para a ocorrência de 03/08/2026 em Taguatinga: "
    "furto de motocicleta Honda CG, placa ABC1D23."
)


def main() -> None:
    load_dotenv()
    print(f"* {AVISO_DADOS}\n")

    loop = LoopReAct(
        llm=llm_padrao(),
        orcamento=Orcamento(max_passos=6, custo_max=20),
        autonomia=Autonomia.AUTONOMO,   # sem pausa para confirmação, para a demo fluir
    )
    traco = loop.executar(TAREFA)
    print(traco.texto_react())


if __name__ == "__main__":
    main()
