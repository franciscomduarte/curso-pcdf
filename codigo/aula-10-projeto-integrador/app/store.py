"""O store compartilhado — herdado sem mudança da Aula 8/9: o checkpoint
HITL vive fora de qualquer pod, num volume compartilhado simulado."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .memoria import Estado

_DIR = Path(__file__).resolve().parent.parent / "saida"


class PausaParaHumano(Exception):
    def __init__(self, checkpoint: str, proposta: dict, pergunta: str) -> None:
        super().__init__(pergunta)
        self.checkpoint = checkpoint
        self.proposta = proposta
        self.pergunta = pergunta


class StoreCompartilhado:
    """Volume compartilhado simulado — qualquer pod lê/escreve o mesmo dado."""

    def __init__(self, diretorio: Path | None = None) -> None:
        self._dir = diretorio or _DIR
        self._dir.mkdir(exist_ok=True)

    def salvar(self, estado: Estado) -> str:
        cid = f"{estado.id}--{uuid.uuid4().hex[:8]}"
        (self._dir / f"{cid}.json").write_text(
            json.dumps(estado.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return cid

    def carregar(self, cid: str) -> Estado:
        caminho = self._dir / f"{cid}.json"
        if not caminho.exists():
            raise FileNotFoundError(f"checkpoint '{cid}' não está no store compartilhado")
        return Estado.from_dict(json.loads(caminho.read_text(encoding="utf-8")))


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
