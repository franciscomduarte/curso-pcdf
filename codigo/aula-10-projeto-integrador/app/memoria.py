"""Memória dos agentes e o estado compartilhado — o mesmo modelo desde a
Aula 7, com um campo novo: `revisao`.

Nas Aulas 7-9, toda ocorrência passava exatamente pelas mesmas 3 etapas
(investigar -> analisar -> juridico) antes do breakpoint humano. Nesta aula,
o roteador (`roteador.py`) pode inserir uma etapa extra — `revisar` — para
casos graves. `revisao` guarda o resultado dessa etapa quando ela acontece;
fica `None` quando o roteador decidiu que não era necessária.
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
    fatos: dict | None = None                 # Investigador
    hipotese: dict | None = None              # Analista
    tipificacao_proposta: dict | None = None  # Jurídico
    revisao: dict | None = None               # Revisor (só quando o roteador escala o caso)
    tipificacao_final: dict | None = None     # Consolidador (após aprovação)
    dossie: dict | None = None                # Consolidador

    etapa: str = "investigar"
    aprovacoes: list[dict] = field(default_factory=list)
    memorias: dict[str, dict] = field(default_factory=dict)
    atendido_por: list[dict] = field(default_factory=list)   # {etapa, pod, duracao_ms} por passo

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
            "tipificacao_proposta": self.tipificacao_proposta, "revisao": self.revisao,
            "tipificacao_final": self.tipificacao_final, "dossie": self.dossie,
            "etapa": self.etapa, "aprovacoes": self.aprovacoes, "memorias": self.memorias,
            "atendido_por": self.atendido_por,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Estado":
        e = cls(id=d["id"], texto=d["texto"])
        for k, v in d.items():
            setattr(e, k, v)
        return e
