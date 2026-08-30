"""Memória dos agentes e o estado compartilhado.

  - Memoria : o "bloco de notas" de UM agente — append-only, para ele consultar
              o que já fez. Cada agente tem a sua.
  - Estado  : o objeto compartilhado que passa por todos os agentes. Cada agente
              lê o que precisa e escreve só a sua parte.

Ambos são serializáveis (dict) para irem no checkpoint.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Memoria:
    dono: str
    notas: list[str] = field(default_factory=list)

    def anotar(self, nota: str) -> None:
        carimbo = datetime.now(timezone.utc).strftime("%H:%M:%S")
        self.notas.append(f"[{carimbo}] {nota}")

    def to_dict(self) -> dict:
        return {"dono": self.dono, "notas": list(self.notas)}

    @classmethod
    def from_dict(cls, d: dict) -> "Memoria":
        return cls(dono=d["dono"], notas=list(d.get("notas", [])))


@dataclass
class Estado:
    id: str
    texto: str
    # cada agente escreve UMA destas chaves:
    fatos: dict | None = None                 # Investigador
    hipotese: dict | None = None              # Analista
    tipificacao_proposta: dict | None = None  # Jurídico
    tipificacao_final: dict | None = None     # Consolidador (após aprovação)
    dossie: dict | None = None                # Consolidador

    # controle do fluxo + HITL
    etapa: str = "investigar"
    aprovacoes: list[dict] = field(default_factory=list)   # trilha das decisões humanas
    memorias: dict[str, dict] = field(default_factory=dict)  # dono -> Memoria.to_dict()

    def memoria_de(self, agente: str) -> Memoria:
        if agente not in self.memorias:
            self.memorias[agente] = Memoria(dono=agente).to_dict()
        return Memoria.from_dict(self.memorias[agente])

    def guardar_memoria(self, m: Memoria) -> None:
        self.memorias[m.dono] = m.to_dict()

    def to_dict(self) -> dict:
        return {
            "id": self.id, "texto": self.texto,
            "fatos": self.fatos, "hipotese": self.hipotese,
            "tipificacao_proposta": self.tipificacao_proposta,
            "tipificacao_final": self.tipificacao_final, "dossie": self.dossie,
            "etapa": self.etapa, "aprovacoes": self.aprovacoes, "memorias": self.memorias,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Estado":
        e = cls(id=d["id"], texto=d["texto"])
        for k, v in d.items():
            setattr(e, k, v)
        return e
