"""O store compartilhado — o checkpoint da Aula 7, agora fora do pod.

Na Aula 7, `Checkpoint.salvar()`/`carregar()` viviam no disco de UM processo:
funcionava porque só havia um processo. Aqui um Deployment pode ter várias
réplicas (pods) atrás do mesmo Service — a próxima chamada pode cair em
QUALQUER uma delas, escolhida por round-robin. Se o estado morasse na
memória de um pod específico, a réplica errada não saberia retomar.

`StoreCompartilhado` simula isso: é externo a qualquer pod (na prática seria
um volume compartilhado — um PVC — ou um banco). Qualquer pod que o consulte
enxerga o mesmo dado, não importa qual réplica atendeu a chamada anterior.
"""

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
