"""Nível básico: o agente enriquece UMA ocorrência consultando o servidor MCP.

    python main.py

Mostra os três níveis lado a lado:
  1. o texto cru (LLM só produziria texto)
  2. o agente decidindo chamar ferramentas
  3. as chamadas passando pelo servidor MCP (com auditoria)
"""

from __future__ import annotations

import logging

from dotenv import load_dotenv

from app.agente_consultor import AgenteConsultor
from app.bases_sinteticas import AVISO_DADOS
from app.cliente_mcp import ClienteMCP
from app.llm import consultor_padrao
from app.servidor_mcp import ServidorMCP

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

OCORRENCIA = (
    "03/08/2026, Taguatinga. Vítima relata furto de uma motocicleta Honda CG, "
    "placa ABC1D23, que estava estacionada na via. Sem testemunhas até o momento."
)


def main() -> None:
    load_dotenv()
    print(f"* {AVISO_DADOS}\n")

    servidor = ServidorMCP()                      # escopo completo
    cliente = ClienteMCP(servidor, nome="agente-consultor")
    agente = AgenteConsultor(cliente=cliente, llm=consultor_padrao())

    print("--- ocorrência (texto) ---")
    print(OCORRENCIA)

    resultado = agente.enriquecer(OCORRENCIA)

    print("\n--- passos do agente (via MCP) ---")
    for obs in resultado.observacoes:
        print(f"  {obs}")
    print(f"\n--- enriquecimento ({resultado.passos} consultas) ---")
    print(resultado.enriquecimento)

    print("\n--- trilha de auditoria do servidor MCP ---")
    print(servidor.trilha())


if __name__ == "__main__":
    main()
