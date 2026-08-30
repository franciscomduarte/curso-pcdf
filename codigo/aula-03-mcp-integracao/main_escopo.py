"""Nível intermediário: autorização por escopo.

    python main_escopo.py

Duas camadas de defesa:
  1. o cliente só "enxerga" as ferramentas que o servidor listou (descoberta);
  2. mesmo que algo tente chamar direto, o servidor NEGA o que está fora do
     escopo — e registra a tentativa.
"""

from __future__ import annotations

import logging

from app.agente_consultor import AgenteConsultor
from app.bases_sinteticas import AVISO_DADOS
from app.cliente_mcp import ClienteMCP
from app.esquema import ChamadaMCP
from app.llm import MockConsultor
from app.servidor_mcp import ServidorMCP

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

OCORRENCIA = (
    "10/08/2026, Asa Norte. Furto de bicicleta na garagem de um prédio, "
    "sem arrombamento. Placa de um carro anotada por vizinho: XYZ9Z87."
)


def main() -> None:
    print(f"* {AVISO_DADOS}\n")

    # escopo restrito: consultar_veiculo NÃO está autorizado
    servidor = ServidorMCP(escopo={"consultar_ocorrencias_similares", "buscar_documento"})
    cliente = ClienteMCP(servidor, nome="agente-triagem-restrito")
    agente = AgenteConsultor(cliente=cliente, llm=MockConsultor())

    print("Camada 1 — o que o agente descobre neste escopo:")
    for spec in cliente.conectar():
        print(f"  - {spec.nome}")

    resultado = agente.enriquecer(OCORRENCIA)
    print("\n--- passos do agente ---")
    for obs in resultado.observacoes:
        print(f"  {obs}")

    print("\nCamada 2 — tentativa direta de chamar a ferramenta fora do escopo:")
    resp = servidor.atender(ChamadaMCP(
        metodo="chamar_ferramenta", ferramenta="consultar_veiculo",
        argumentos={"placa": "XYZ9Z87"}, cliente="processo-desonesto",
    ))
    print(f"  resposta do servidor: ok={resp.ok} erro={resp.erro!r}")

    print("\n--- trilha (repare no [NEG]) ---")
    print(servidor.trilha())


if __name__ == "__main__":
    main()
