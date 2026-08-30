"""Dados sintéticos e lógica mínima (determinística) de extração/classificação.

>>> Todos os dados são FICTÍCIOS e destinados exclusivamente ao treinamento.

Na Aula 2 o foco é *comunicação*, não a qualidade da extração. Por isso aqui
tudo é regra fixa e offline — o que interessa é como o resultado trafega entre
os agentes.
"""

from __future__ import annotations

import re

AVISO_DADOS = (
    "Todos os dados desta aula são FICTÍCIOS e destinados exclusivamente ao treinamento."
)

OCORRENCIAS_BRUTAS: list[dict[str, str]] = [
    {"id": "PCDF-SIM-0001", "texto":
        "15/08/2026, Asa Norte. A comunicante Marina Alves relata que seu notebook "
        "e uma bicicleta foram subtraídos da garagem, sem arrombamento."},
    {"id": "PCDF-SIM-0002", "texto":
        "03/08/2026, Taguatinga. A vítima Rafael Souza informa que dois indivíduos "
        "em motocicleta anunciaram assalto e levaram seu celular, com simulacro de arma."},
    {"id": "PCDF-SIM-0003", "texto":
        "10/08/2026, Guará. A comunicante Beatriz Lima recebe mensagens intimidatórias "
        "de um ex-colega, com ameaças de agressão."},
    {"id": "PCDF-SIM-0004", "texto":
        "22/07/2026, Lago Sul. Henrique Prado comunica que um veículo teve os pneus "
        "furados e a lataria riscada durante a madrugada."},
    {"id": "PCDF-SIM-0005", "texto":
        "05/08/2026, Ceilândia. A vítima Carla Menezes fez um Pix para um anúncio "
        "falso de venda de celular; o produto nunca foi entregue."},
]

_REGRAS = [
    ("Roubo", ("assalto", "simulacro", "arma", "mediante")),
    ("Furto", ("subtraíd", "furt", "sem arrombamento")),
    ("Ameaça", ("ameaç", "intimidat")),
    ("Dano", ("furad", "riscad", "danific")),
    ("Estelionato", ("pix", "anúncio falso", "golpe", "nunca foi entregue")),
]
_REGIOES = ("Asa Norte", "Asa Sul", "Taguatinga", "Ceilândia", "Guará", "Lago Sul", "Gama")


def extrair(texto: str) -> dict:
    """Texto livre -> dicionário estruturado (o 'conteudo' do envelope)."""
    t = texto.lower()
    natureza = next((n for n, gs in _REGRAS if any(g in t for g in gs)), "Outros")
    data = None
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", texto)
    if m:
        d, mes, ano = m.groups()
        data = f"{ano}-{mes}-{d}"
    local = next((r for r in _REGIOES if r.lower() in t), None)
    return {"natureza": natureza, "data_fato": data, "local": local,
            "resumo": re.split(r"(?<=[.!?])\s+", texto.strip())[0][:200]}


SENSIVEIS = {"Roubo", "Lesão corporal"}


def classificar(conteudo: dict) -> dict:
    """Decide prioridade e se precisa de revisão humana obrigatória."""
    natureza = conteudo.get("natureza", "Outros")
    revisar = natureza in SENSIVEIS or natureza == "Outros"
    if not conteudo.get("local") or not conteudo.get("data_fato"):
        revisar = True
    prioridade = "alta" if natureza in SENSIVEIS else "normal"
    return {"natureza": natureza, "prioridade": prioridade,
            "revisao_humana_obrigatoria": revisar}
