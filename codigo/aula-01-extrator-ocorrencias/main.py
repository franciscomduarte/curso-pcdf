"""Nível básico: extrai UMA ocorrência sintética e imprime o resultado.

    python main.py            # primeira ocorrência sintética
    python main.py PCDF-SIM-0003
"""

from __future__ import annotations

import logging
import sys

from dotenv import load_dotenv

from app.agente_extrator import AgenteExtrator
from app.dados_sinteticos import AVISO_DADOS, OCORRENCIAS_BRUTAS, por_id
from app.llm import extrator_padrao

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main() -> None:
    load_dotenv()
    print(f"* {AVISO_DADOS}\n")

    item = por_id(sys.argv[1]) if len(sys.argv) > 1 else OCORRENCIAS_BRUTAS[0]
    llm = extrator_padrao()
    print(f"Extrator em uso: {type(llm).__name__}\n")

    agente = AgenteExtrator(llm=llm)
    ocorrencia = agente.processar(item["id"], item["texto"])

    print(f"--- {item['id']} ---")
    print(item["texto"])
    print("\n--- estruturado ---")
    print(ocorrencia.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
