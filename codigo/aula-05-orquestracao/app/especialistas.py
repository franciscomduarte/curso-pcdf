"""Os agentes especialistas do SIGMA.

Cada um: recebe o `Dossie` (estado compartilhado), faz a sua parte, devolve o
Dossie atualizado e registra métricas. A metadata (`precisa` / `produz`) é o que
permite ao Broker e ao Blackboard decidirem sozinhos a ordem.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .bases_sinteticas import consultar_similares, consultar_veiculo, extrair_campos
from .metricas import Metricas


@dataclass
class Dossie:
    id: str
    texto: str
    campos: dict | None = None
    classificacao: dict | None = None
    enriquecimento: list | None = None
    revisado: bool = False
    pendencias: list[str] = field(default_factory=list)
    completo: bool = False

    def tem(self, campo: str) -> bool:
        return getattr(self, campo, None) not in (None, [], False)


# --- especialistas ------------------------------------------------------
def extrator(d: Dossie, m: Metricas) -> Dossie:
    d.campos = extrair_campos(d.texto)
    m.registrar(especialista=True, llm=1, custo=2, latencia_ms=400)
    return d


def classificador(d: Dossie, m: Metricas) -> Dossie:
    c = d.campos or {}
    natureza = "Roubo" if c.get("tem_violencia") else "Furto"
    prioridade = "alta" if natureza == "Roubo" else "normal"
    d.classificacao = {"natureza": natureza, "prioridade": prioridade}
    m.registrar(especialista=True, llm=1, custo=1, latencia_ms=300)
    return d


def consultor(d: Dossie, m: Metricas) -> Dossie:
    c = d.campos or {}
    achados = []
    if c.get("placa_citada"):
        achados.append(consultar_veiculo(c["placa_citada"]))
        m.registrar(ferramentas=1, custo=2, latencia_ms=250)
    if c.get("local"):
        achados.append({"similares": consultar_similares(c["local"])})
        m.registrar(ferramentas=1, custo=2, latencia_ms=250)
    d.enriquecimento = achados
    m.registrar(especialista=True, llm=1, custo=1, latencia_ms=200)
    return d


def revisor(d: Dossie, m: Metricas) -> Dossie:
    pend = []
    if not d.tem("campos"):
        pend.append("campos não extraídos")
    if not d.tem("classificacao"):
        pend.append("sem classificação")
    if not d.tem("enriquecimento"):
        pend.append("sem enriquecimento (pode ser aceitável)")
    if d.classificacao and d.campos:
        viol = d.campos.get("tem_violencia")
        if viol and d.classificacao["natureza"] == "Furto":
            pend.append("incoerência: há violência mas foi classificado Furto")
    d.pendencias = pend
    d.completo = not [p for p in pend if "aceitável" not in p]
    d.revisado = True
    m.registrar(especialista=True, llm=1, custo=1, latencia_ms=300)
    return d


@dataclass
class SpecEspecialista:
    nome: str
    precisa: set[str]
    produz: str
    funcao: object


REGISTRO: dict[str, SpecEspecialista] = {
    "extrator": SpecEspecialista("extrator", set(), "campos", extrator),
    "classificador": SpecEspecialista("classificador", {"campos"}, "classificacao", classificador),
    "consultor": SpecEspecialista("consultor", {"campos"}, "enriquecimento", consultor),
    "revisor": SpecEspecialista("revisor", {"campos", "classificacao"}, "revisado", revisor),
}

ORDEM_PIPELINE = ["extrator", "classificador", "consultor", "revisor"]
