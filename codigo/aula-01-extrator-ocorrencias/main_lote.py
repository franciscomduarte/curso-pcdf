"""Nível avançado: processa TODAS as ocorrências sintéticas, persiste o
resultado e imprime um relatório consolidado.

    python main_lote.py

Saídas em ./saida/resultados.json e ./saida/relatorio.txt
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from dotenv import load_dotenv

from app.agente_extrator import AgenteExtrator
from app.dados_sinteticos import AVISO_DADOS, OCORRENCIAS_BRUTAS
from app.llm import extrator_padrao
from app.relatorio import consolidar, formatar

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

SAIDA = Path(__file__).parent / "saida"


def main() -> None:
    load_dotenv()
    print(f"* {AVISO_DADOS}\n")

    agente = AgenteExtrator(llm=extrator_padrao())

    ocorrencias = []
    registros = []
    for item in OCORRENCIAS_BRUTAS:
        oc = agente.processar(item["id"], item["texto"])
        ocorrencias.append(oc)
        registros.append({"id": item["id"], **oc.model_dump()})

    SAIDA.mkdir(exist_ok=True)
    (SAIDA / "resultados.json").write_text(
        json.dumps(registros, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    relatorio = consolidar(ocorrencias)
    texto = formatar(relatorio)
    (SAIDA / "relatorio.txt").write_text(texto + "\n", encoding="utf-8")

    print(texto)
    print(f"\nArquivos gravados em {SAIDA}/")


if __name__ == "__main__":
    main()
